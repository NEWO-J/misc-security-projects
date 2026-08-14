const TAU = Math.PI * 2;
const FONT = '"Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif';

const ENTITY_TYPES = {
    Incident:    { icon: 'shield',  colorVar: '--node-incident', kind: 'Incident', radius: 30,
                   title: (p) => `Incident ${p.incident_id}` },
    TorExitNode: { icon: 'host',    colorVar: '--node-tor',      kind: 'Tor exit node', radius: 26,
                   title: (p) => p.ip },
    User:        { icon: 'user',    colorVar: '--node-user',     kind: 'User account', radius: 24,
                   title: (p) => p.username },
    Host:        { icon: 'host',    colorVar: '--node-host',     kind: 'Host',    radius: 24,
                   title: (p) => p.ip },
    Service:     { icon: 'service', colorVar: '--node-service',  kind: 'Service', radius: 24,
                   title: (p) => p.service },
};

const TYPE_PRIORITY = ['Incident', 'User', 'Host', 'Service'];

const FALLBACK_TYPE = {
    icon: 'dot', colorVar: '--node-other', kind: 'Entity', radius: 22,
    title: (p) => p.name || p.id || 'Unknown',
};

const RELATION_LABELS = {
    INCIDENT: 'Involves',
    FROM_HOST: 'Origin of',
    ACCESSING_SERVICE: 'Accessing',
};

const SEVERITIES = [
    { min: 20, name: 'High',          cls: 'sev-high', colorVar: '--sev-high' },
    { min: 10, name: 'Medium',        cls: 'sev-med',  colorVar: '--sev-med'  },
    { min: 5,  name: 'Low',           cls: 'sev-low',  colorVar: '--sev-low'  },
    { min: 0,  name: 'Informational', cls: 'sev-info', colorVar: '--sev-info' },
];

const INCIDENT_TYPES = {
    1010: {
        title: 'Repeated failed sign-ins on a single account',
        tags: ['Brute force', 'Identity'],
        severity: (row) => severityByAttempts(row.login_attempts),
        summary: (row) => `${row.login_attempts ?? 0} attempts`,
    },
    1011: {
        title: 'Sign-in from a Tor exit node',
        tags: ['Anonymised network', 'Initial access'],
        severity: () => severityNamed('High'),
        summary: () => 'Tor exit node',
    },
    1012: {
        title: 'Password spray from a single host',
        tags: ['Password spray', 'Credential access'],
        severity: (row) => severityByAccounts(row.affected_users_count),
        summary: (row) => `${row.affected_users_count ?? 0} accounts targeted`,
    },
};

const DEFAULT_INCIDENT_TYPE = {
    title: 'Identity incident',
    tags: ['Identity'],
    severity: (row) => severityByAttempts(row.login_attempts),
    summary: (row) => (row.login_attempts == null ? '' : `${row.login_attempts} attempts`),
};

const PALETTE = {};
const state = {
    network: null,
    graph: { nodes: [], edges: [] },
    nodeMeta: new Map(),
    incidentId: null,
    incident: null,
    seeds: [],
    selectedId: null,
    view: 'graph',
};

const $ = (sel) => document.querySelector(sel);

function readPalette() {
    const css = getComputedStyle(document.documentElement);
    const keys = [
        'canvas', 'surface', 'surface-alt', 'surface-raise', 'border', 'text', 'text-2', 'text-3',
        'accent', 'node-incident', 'node-user', 'node-host', 'node-service', 'node-tor', 'node-other',
        'node-fill', 'edge', 'sev-high', 'sev-med', 'sev-low', 'sev-info',
    ];
    keys.forEach((key) => { PALETTE[key] = css.getPropertyValue(`--${key}`).trim(); });
}

function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function alpha(hex, a) {
    const value = hex.replace('#', '');
    const full = value.length === 3 ? value.split('').map((c) => c + c).join('') : value;
    const num = parseInt(full, 16);
    return `rgba(${(num >> 16) & 255}, ${(num >> 8) & 255}, ${num & 255}, ${a})`;
}

function typeOf(node) {
    const labels = node.labels || [];
    for (const label of TYPE_PRIORITY) {
        if (labels.includes(label)) return ENTITY_TYPES[label];
    }
    return FALLBACK_TYPE;
}

function severityByAttempts(attempts) {
    const count = Number(attempts) || 0;
    return SEVERITIES.find((s) => count >= s.min);
}

function severityNamed(name) {
    return SEVERITIES.find((s) => s.name === name);
}

function severityByAccounts(count) {
    const accounts = Number(count) || 0;
    if (accounts >= 10) return severityNamed('High');
    if (accounts >= 5) return severityNamed('Medium');
    return severityNamed('Low');
}

function incidentTypeFor(incidentId) {
    return INCIDENT_TYPES[String(incidentId)] || DEFAULT_INCIDENT_TYPE;
}

function severityFor(row) {
    return incidentTypeFor(row.incident_id).severity(row);
}

function relationLabel(type) {
    return RELATION_LABELS[type] || type.toLowerCase().replace(/_/g, ' ');
}

function formatTimestamp(value) {
    if (!value) return null;
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    return date.toLocaleString(undefined, {
        month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit',
    });
}

function relativeTime(value) {
    const date = new Date(value);
    if (!value || Number.isNaN(date.getTime())) return '';
    const seconds = Math.round((Date.now() - date.getTime()) / 1000);
    const units = [['d', 86400], ['h', 3600], ['m', 60]];
    if (seconds < 60) return 'just now';
    for (const [suffix, size] of units) {
        if (Math.abs(seconds) >= size) return `${Math.round(seconds / size)}${suffix} ago`;
    }
    return '';
}

function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
}

const GLYPHS = {
    shield(ctx) {
        ctx.beginPath();
        ctx.moveTo(12, 2.6);
        ctx.lineTo(20, 5.6);
        ctx.lineTo(20, 11.6);
        ctx.bezierCurveTo(20, 16.6, 16.6, 20.4, 12, 21.8);
        ctx.bezierCurveTo(7.4, 20.4, 4, 16.6, 4, 11.6);
        ctx.lineTo(4, 5.6);
        ctx.closePath();
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(12, 8.4);
        ctx.lineTo(12, 13.4);
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(12, 16.6, 1.05, 0, TAU);
        ctx.fill();
    },
    user(ctx) {
        ctx.beginPath();
        ctx.arc(12, 8.8, 3.7, 0, TAU);
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(12, 20.4, 6.4, Math.PI, TAU);
        ctx.stroke();
    },
    host(ctx) {
        roundRect(ctx, 3.2, 4.4, 17.6, 11.6, 1.8);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(12, 16);
        ctx.lineTo(12, 19.4);
        ctx.moveTo(8.4, 19.6);
        ctx.lineTo(15.6, 19.6);
        ctx.stroke();
    },
    service(ctx) {
        roundRect(ctx, 3.4, 4.6, 17.2, 6.2, 1.6);
        ctx.stroke();
        roundRect(ctx, 3.4, 13.2, 17.2, 6.2, 1.6);
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(7.2, 7.7, 1.05, 0, TAU);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(7.2, 16.3, 1.05, 0, TAU);
        ctx.fill();
    },
    dot(ctx) {
        ctx.beginPath();
        ctx.arc(12, 12, 5.4, 0, TAU);
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(12, 12, 1.6, 0, TAU);
        ctx.fill();
    },
};

function drawGlyph(ctx, name, cx, cy, size, color) {
    const glyph = GLYPHS[name] || GLYPHS.dot;
    const scale = size / 24;
    ctx.save();
    ctx.translate(cx - size / 2, cy - size / 2);
    ctx.scale(scale, scale);
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.lineWidth = 1.8;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    glyph(ctx);
    ctx.restore();
}

function nodeRenderer({ ctx, id, x, y, state: visState }) {
    const meta = state.nodeMeta.get(id) || {};
    const radius = meta.radius || 22;
    const accent = meta.accent || PALETTE['node-other'];
    const active = visState.selected || visState.hover;

    return {
        drawNode() {
            if (active) {
                ctx.beginPath();
                ctx.arc(x, y, radius + 7, 0, TAU);
                ctx.fillStyle = alpha(accent, visState.selected ? 0.20 : 0.11);
                ctx.fill();
                ctx.lineWidth = 1;
                ctx.strokeStyle = alpha(accent, visState.selected ? 0.85 : 0.4);
                ctx.stroke();
            }

            if (meta.alerted) {
                ctx.beginPath();
                ctx.arc(x, y, radius + 4.5, 0, TAU);
                ctx.fillStyle = alpha(accent, 0.16);
                ctx.fill();
                ctx.lineWidth = 1.5;
                ctx.strokeStyle = alpha(accent, 0.6);
                ctx.stroke();
            }

            ctx.beginPath();
            ctx.arc(x, y, radius, 0, TAU);
            ctx.fillStyle = PALETTE['node-fill'];
            ctx.fill();
            ctx.lineWidth = meta.isSeed || meta.alerted ? 2.5 : 2;
            ctx.strokeStyle = accent;
            ctx.stroke();

            drawGlyph(ctx, meta.icon, x, y, radius * 1.08, accent);
        },

        drawExternalLabel() {
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';

            ctx.font = `600 12px ${FONT}`;
            ctx.fillStyle = PALETTE.text;
            ctx.fillText(meta.title || '', x, y + radius + 9);

            ctx.font = `400 11px ${FONT}`;
            ctx.fillStyle = PALETTE['text-3'];
            ctx.fillText(meta.kind || '', x, y + radius + 25);
        },

        nodeDimensions: { width: radius * 2, height: radius * 2 },
    };
}

function buildNodeMeta(graph) {
    const meta = new Map();
    const incident = state.incident || {};
    const torIp = incident.tor_exit ? incident.source_ip : null;

    graph.nodes.forEach((node) => {
        const props = node.properties || {};
        const labels = node.labels || [];
        const isTor = torIp != null && labels.includes('Host') && props.ip === torIp;
        const type = isTor ? ENTITY_TYPES.TorExitNode : typeOf(node);

        meta.set(node.id, {
            icon: type.icon,
            kind: type.kind,
            radius: type.radius,
            accent: cssVar(type.colorVar),
            title: String(type.title(props) ?? '—'),
            isSeed: state.seeds.includes(node.id),
            alerted: isTor,
            labels,
            properties: props,
        });
    });

    return meta;
}

function renderGraph(graph) {
    state.graph = graph;
    state.nodeMeta = buildNodeMeta(graph);

    const nodes = new vis.DataSet(graph.nodes.map((node) => {
        const meta = state.nodeMeta.get(node.id);
        return {
            id: node.id,
            shape: 'custom',
            ctxRenderer: nodeRenderer,
            size: meta.radius,
            mass: meta.isSeed ? 3 : 1,
        };
    }));

    const edges = new vis.DataSet(graph.edges.map((edge) => ({
        id: edge.id,
        from: edge.source,
        to: edge.target,
        label: relationLabel(edge.type),
    })));

    const container = $('#graph-container');
    const options = {
        autoResize: true,
        layout: { improvedLayout: true, randomSeed: 7 },
        nodes: { labelHighlightBold: false },
        edges: {
            color: { color: PALETTE.edge, highlight: PALETTE.accent, hover: PALETTE.accent, inherit: false },
            width: 1.4,
            selectionWidth: 1,
            hoverWidth: 0.4,
            smooth: false,
            arrows: { to: { enabled: true, scaleFactor: 0.5, type: 'arrow' } },
            font: {
                size: 10.5,
                face: FONT,
                color: PALETTE['text-3'],
                strokeWidth: 0,
                background: PALETTE.surface,
                align: 'middle',
            },
        },
        physics: {
            solver: 'barnesHut',
            barnesHut: {
                gravitationalConstant: -9000,
                centralGravity: 0.45,
                springLength: 185,
                springConstant: 0.05,
                damping: 0.4,
                avoidOverlap: 0.35,
            },
            stabilization: { enabled: true, iterations: 400, fit: true },
        },
        interaction: {
            hover: true,
            dragNodes: true,
            navigationButtons: false,
            keyboard: false,
            zoomView: true,
        },
    };

    if (state.network) state.network.destroy();
    state.network = new vis.Network(container, { nodes, edges }, options);

    state.network.once('stabilizationIterationsDone', () => {
        state.network.setOptions({ physics: { enabled: false } });
        state.network.fit({ animation: { duration: 350, easingFunction: 'easeOutQuad' } });
    });

    state.network.on('click', (params) => {
        if (params.nodes.length) selectEntity(params.nodes[0]);
        else if (params.edges.length) selectRelationship(params.edges[0]);
        else clearSelection();
    });
}

function relayout() {
    if (!state.network) return;
    state.network.setOptions({ physics: { enabled: true } });
    state.network.stabilize(400);
    state.network.once('stabilizationIterationsDone', () => {
        state.network.setOptions({ physics: { enabled: false } });
        state.network.fit({ animation: { duration: 350, easingFunction: 'easeOutQuad' } });
    });
}

function countByKind(kind) {
    let total = 0;
    state.nodeMeta.forEach((meta) => { if (meta.kind === kind) total += 1; });
    return total;
}

function renderIncidentHeader() {
    const incident = state.incident;
    const title = $('#incident-title');
    const meta = $('#incident-meta');
    const badges = $('#incident-badges');
    const bar = $('#incident-sev-bar');

    if (!incident) {
        title.textContent = 'No incident selected';
        meta.textContent = 'Pick an incident from the queue, or search by ID.';
        badges.innerHTML = '';
        bar.style.background = 'var(--text-3)';
        return;
    }

    const props = incident;
    const severity = severityFor(props);
    const type = incidentTypeFor(props.incident_id);
    const when = formatTimestamp(props.incident_date);

    title.textContent = type.title;

    const bits = [`Incident ${props.incident_id}`];
    if (when) bits.push(when);
    bits.push(`${state.graph.nodes.length} entities`, `${state.graph.edges.length} relationships`);
    meta.innerHTML = bits.map((bit) => `<span>${escapeHtml(bit)}</span>`).join('<span class="dot"></span>');

    badges.innerHTML = [
        `<span class="pill ${severity.cls}">${severity.name}</span>`,
        ...type.tags.map((tag) => `<span class="pill pill-plain">${escapeHtml(tag)}</span>`),
    ].join('');
    bar.style.background = cssVar(severity.colorVar);
}

const HOST_ICON = '<rect x="3.2" y="4.6" width="17.6" height="11.4" rx="1.8"/><path d="M12 16v3.4M8.4 19.6h7.2"/>';

const TILE_ICONS = {
    attempts: '<path d="M12 3v9l5 3"/><circle cx="12" cy="12" r="9"/>',
    logins: '<path d="M10 4.6H6.2a1.6 1.6 0 0 0-1.6 1.6v11.6a1.6 1.6 0 0 0 1.6 1.6H10"/><path d="M14.6 8.4 18.8 12l-4.2 3.6M18.4 12H9.2"/>',
    Incident: '<path d="M12 2.6 20 5.6v6c0 5-3.4 8.8-8 10.2-4.6-1.4-8-5.2-8-10.2v-6Z"/><path d="M12 8.4v5"/><circle cx="12" cy="16.6" r=".9" fill="currentColor"/>',
    User: '<circle cx="12" cy="8.5" r="3.6"/><path d="M5.6 20a6.4 6.4 0 0 1 12.8 0"/>',
    Host: HOST_ICON,
    Service: '<rect x="3.4" y="4.6" width="17.2" height="6" rx="1.5"/><rect x="3.4" y="13.4" width="17.2" height="6" rx="1.5"/>',
    'Tor exit node': HOST_ICON,
};

function renderTiles() {
    const incident = state.incident;
    const tiles = $('#tiles');

    if (!incident) { tiles.innerHTML = ''; return; }

    const attempts = incident.login_attempts;
    const successful = incident.successful_logins;
    const torHosts = countByKind('Tor exit node');

    const rows = [];

    if (attempts != null) {
        rows.push({ label: 'Failed attempts', value: attempts,
                    icon: TILE_ICONS.attempts, color: cssVar(severityFor(incident).colorVar) });
    }
    if (successful != null) {
        rows.push({ label: 'Successful logins', value: successful,
                    icon: TILE_ICONS.logins, color: cssVar('--node-host') });
    }
    if (torHosts) {
        rows.push({ label: 'Tor exit nodes', value: torHosts,
                    icon: TILE_ICONS['Tor exit node'], color: cssVar('--node-tor') });
    }

    rows.push(
        { label: 'Accounts', value: countByKind('User account'), icon: TILE_ICONS.User, color: cssVar('--node-user') },
        { label: 'Hosts',    value: countByKind('Host') + torHosts, icon: TILE_ICONS.Host, color: cssVar('--node-host') },
        { label: 'Services', value: countByKind('Service'),      icon: TILE_ICONS.Service, color: cssVar('--node-service') },
    );

    tiles.innerHTML = rows.map((row) => `
        <div class="tile">
            <span class="tile-icon" style="color:${row.color};background:${alpha(row.color, 0.14)}">
                <svg viewBox="0 0 24 24">${row.icon}</svg>
            </span>
            <span>
                <span class="tile-value">${escapeHtml(String(row.value))}</span>
                <span class="tile-label${row.label.length > 15 ? ' is-long' : ''}">${row.label}</span>
            </span>
        </div>`).join('');
}

function connectionsFor(nodeId) {
    return state.graph.edges
        .filter((edge) => edge.source === nodeId || edge.target === nodeId)
        .map((edge) => {
            const otherId = edge.source === nodeId ? edge.target : edge.source;
            return {
                id: otherId,
                meta: state.nodeMeta.get(otherId),
                relation: relationLabel(edge.type),
                outbound: edge.source === nodeId,
            };
        })
        .filter((conn) => conn.meta);
}

function selectEntity(nodeId) {
    const meta = state.nodeMeta.get(nodeId);
    if (!meta) return;

    state.selectedId = nodeId;
    if (state.network) {
        state.network.selectNodes([nodeId], false);
        state.network.focus(nodeId, { scale: state.network.getScale(), animation: { duration: 300 } });
    }

    const props = Object.entries(meta.properties);
    const connections = connectionsFor(nodeId);
    const glyphSvg = TILE_ICONS[meta.kind === 'User account' ? 'User' : meta.kind] || TILE_ICONS.attempts;

    $('#details-panel').innerHTML = `
        <div class="details-head">
            <span class="details-avatar" style="color:${meta.accent}">
                <svg viewBox="0 0 24 24">${glyphSvg}</svg>
            </span>
            <span>
                <div class="details-title">${escapeHtml(meta.title)}</div>
                <div class="details-type">${escapeHtml(meta.kind)}</div>
            </span>
        </div>

        ${meta.alerted ? `
        <div class="details-section">
            <h3>Reputation</h3>
            <span class="pill sev-high">Tor exit node</span>
            <div class="overlay-text" style="margin-top:8px">This address is published on the Tor exit-node
            list, so the true origin of the sign-in is hidden.</div>
        </div>` : ''}

        <div class="details-section">
            <h3>Properties</h3>
            <dl class="kv">
                ${props.length
                    ? props.map(([key, value]) => `
                        <dt>${escapeHtml(key)}</dt>
                        <dd class="mono">${escapeHtml(formatValue(key, value))}</dd>`).join('')
                    : '<dd class="muted">No properties</dd>'}
            </dl>
        </div>

        <div class="details-section">
            <h3>Connections (${connections.length})</h3>
            <div class="conn-list">
                ${connections.length
                    ? connections.map((conn) => `
                        <button class="conn" data-node="${escapeHtml(conn.id)}">
                            <span class="entity-dot" style="color:${conn.meta.accent}"></span>
                            <span>${escapeHtml(conn.meta.title)}</span>
                            <span class="conn-rel">${escapeHtml(conn.outbound ? conn.relation : `${conn.relation} →`)}</span>
                        </button>`).join('')
                    : '<span class="muted">No related entities</span>'}
            </div>
        </div>`;

    $('#details-panel').querySelectorAll('.conn').forEach((button) => {
        button.addEventListener('click', () => selectEntity(button.dataset.node));
    });
}

function selectRelationship(edgeId) {
    const edge = state.graph.edges.find((candidate) => candidate.id === edgeId);
    if (!edge) return;

    const source = state.nodeMeta.get(edge.source);
    const target = state.nodeMeta.get(edge.target);
    state.selectedId = null;

    $('#details-panel').innerHTML = `
        <div class="details-head">
            <span class="details-avatar" style="color:${cssVar('--accent')}">
                <svg viewBox="0 0 24 24"><path d="M5 12h14M14 7l5 5-5 5"/></svg>
            </span>
            <span>
                <div class="details-title">${escapeHtml(relationLabel(edge.type))}</div>
                <div class="details-type">Relationship</div>
            </span>
        </div>
        <div class="details-section">
            <h3>Path</h3>
            <div class="conn-list">
                <button class="conn" data-node="${escapeHtml(edge.source)}">
                    <span class="entity-dot" style="color:${source?.accent}"></span>
                    <span>${escapeHtml(source?.title || edge.source)}</span>
                    <span class="conn-rel">Source</span>
                </button>
                <button class="conn" data-node="${escapeHtml(edge.target)}">
                    <span class="entity-dot" style="color:${target?.accent}"></span>
                    <span>${escapeHtml(target?.title || edge.target)}</span>
                    <span class="conn-rel">Target</span>
                </button>
            </div>
        </div>`;

    $('#details-panel').querySelectorAll('.conn').forEach((button) => {
        button.addEventListener('click', () => selectEntity(button.dataset.node));
    });
}

function clearSelection() {
    state.selectedId = null;
    if (state.network) state.network.unselectAll();

    const incident = state.incident;
    $('#details-panel').innerHTML = `
        <div class="details-empty">
            <svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="6" cy="6" r="2.6"/><circle cx="18" cy="7" r="2.6"/><circle cx="12" cy="18" r="2.6"/>
                <path d="M8.2 7.2 15.6 6.6M7.2 8.2l3.8 7.6M16.8 9.4l-3.4 6.4"/>
            </svg>
            <div>${incident ? 'Select an entity or relationship' : 'No incident loaded'}</div>
            <div class="overlay-text">${incident
                ? 'Click any node in the attack story to inspect its properties and connections.'
                : 'Load an incident to start investigating.'}</div>
        </div>`;
}

function renderAssets() {
    const rows = [...state.nodeMeta.entries()]
        .sort((a, b) => a[1].kind.localeCompare(b[1].kind) || a[1].title.localeCompare(b[1].title))
        .map(([id, meta]) => {
            const links = connectionsFor(id).length;
            const detail = meta.properties.incident_date
                ? formatTimestamp(meta.properties.incident_date)
                : Object.entries(meta.properties).map(([k, v]) => `${k}=${v}`).join(', ');

            return `
                <tr data-node="${escapeHtml(id)}">
                    <td>
                        <span class="entity-cell">
                            <span class="entity-dot" style="color:${meta.accent}"></span>
                            ${escapeHtml(meta.title)}
                        </span>
                    </td>
                    <td class="muted">${escapeHtml(meta.kind)}</td>
                    <td class="mono muted">${escapeHtml(detail || '—')}</td>
                    <td class="muted">${links}</td>
                </tr>`;
        });

    $('#assets-view').innerHTML = rows.length ? `
        <table class="assets">
            <thead>
                <tr><th>Entity</th><th>Type</th><th>Details</th><th>Links</th></tr>
            </thead>
            <tbody>${rows.join('')}</tbody>
        </table>` : '<div class="queue-empty">No entities loaded.</div>';

    $('#assets-view').querySelectorAll('tbody tr').forEach((row) => {
        row.addEventListener('click', () => {
            switchView('graph');
            selectEntity(row.dataset.node);
        });
    });
}

function switchView(view) {
    state.view = view;
    document.querySelectorAll('.tab').forEach((tab) => {
        tab.classList.toggle('is-active', tab.dataset.view === view);
    });
    $('#stage').hidden = view !== 'graph';
    $('#assets-view').hidden = view !== 'assets';
    if (view === 'graph' && state.network) state.network.redraw();
}

function showOverlay(html) {
    const overlay = $('#stage-overlay');
    overlay.innerHTML = html;
    overlay.hidden = false;
}

function hideOverlay() {
    $('#stage-overlay').hidden = true;
}

async function loadIncident(incidentId) {
    const id = String(incidentId || '').trim();
    if (!id) return;

    state.incidentId = id;
    switchView('graph');
    showOverlay('<div class="spinner"></div><div class="overlay-text">Building attack story…</div>');
    markActiveQueueItem(id);

    try {
        const response = await fetch(`/incidents/${encodeURIComponent(id)}?depth=2`);

        if (response.status === 404) {
            showOverlay(`
                <div class="overlay-title">Incident not found</div>
                <div class="overlay-text">No incident with ID <code>${escapeHtml(id)}</code> exists in the graph.</div>`);
            return;
        }
        if (!response.ok) throw new Error(`Server responded with ${response.status}`);

        const json = await response.json();
        if (json.status !== 'success' || !json.data) throw new Error('Malformed response');

        state.incident = json.incident || {};
        state.seeds = json.seeds || [];

        renderGraph(json.data);
        renderIncidentHeader();
        renderTiles();
        renderAssets();
        clearSelection();
        hideOverlay();

        if (!json.data.edges.length) {
            showOverlay(`
                <div class="overlay-title">Isolated incident</div>
                <div class="overlay-text">This incident has no linked entities yet — the graph connector may not have
                processed its related users, hosts or services.</div>`);
        }
    } catch (error) {
        console.error('Failed to load incident graph:', error);
        showOverlay(`
            <div class="overlay-title">Could not load incident</div>
            <div class="overlay-text">${escapeHtml(error.message)}. Check that the dashboard backend and Neo4j
            are reachable.</div>`);
    }
}

function markActiveQueueItem(id) {
    document.querySelectorAll('.queue-item').forEach((item) => {
        item.classList.toggle('is-active', item.dataset.incident === String(id));
    });
}

async function loadQueue() {
    const list = $('#queue-list');
    list.innerHTML = '<div class="queue-empty">Loading incidents…</div>';

    try {
        const response = await fetch('/incidents?limit=50');
        if (!response.ok) throw new Error(`Server responded with ${response.status}`);

        const json = await response.json();
        const incidents = json.data || [];
        $('#queue-count').textContent = incidents.length;

        if (!incidents.length) {
            list.innerHTML = '<div class="queue-empty">No incidents in the graph yet.</div>';
            return;
        }

        list.innerHTML = incidents.map((incident) => {
            const severity = severityFor(incident);
            const type = incidentTypeFor(incident.incident_id);
            const users = (incident.users || []).filter(Boolean);
            const meta = [
                users[0] || 'Unknown account',
                `ID ${incident.incident_id}`,
                type.summary(incident),
                relativeTime(incident.incident_date),
            ].filter(Boolean);

            return `
                <button class="queue-item" data-incident="${escapeHtml(incident.incident_id)}">
                    <div class="queue-item-top">
                        <span class="pill ${severity.cls}">${severity.name}</span>
                        <span class="queue-item-title" title="${escapeHtml(type.title)}">${escapeHtml(type.title)}</span>
                    </div>
                    <div class="queue-item-sub">
                        ${meta.map((bit) => `<span>${escapeHtml(bit)}</span>`).join('<span class="dot"></span>')}
                    </div>
                </button>`;
        }).join('');

        list.querySelectorAll('.queue-item').forEach((item) => {
            item.addEventListener('click', () => {
                $('#incident-input').value = item.dataset.incident;
                loadIncident(item.dataset.incident);
            });
        });

        markActiveQueueItem(state.incidentId);
    } catch (error) {
        console.error('Failed to load incident queue:', error);
        list.innerHTML = '<div class="queue-empty">Incident queue unavailable.</div>';
    }
}

function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, (char) => (
        { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]
    ));
}

function formatValue(key, value) {
    if (key.endsWith('_date') || key === 'ts') return formatTimestamp(value) || String(value);
    return String(value);
}

function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem('iam-graph-theme', theme);
    readPalette();

    if (state.network) {
        state.nodeMeta = buildNodeMeta(state.graph);
        state.network.setOptions({
            edges: {
                color: { color: PALETTE.edge, highlight: PALETTE.accent, hover: PALETTE.accent, inherit: false },
                font: { color: PALETTE['text-3'], background: PALETTE.surface },
            },
        });
        state.network.redraw();
        renderTiles();
        renderAssets();
        if (state.selectedId) selectEntity(state.selectedId);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    readPalette();
    applyTheme(localStorage.getItem('iam-graph-theme') || 'dark');
    clearSelection();

    const input = $('#incident-input');

    $('#load-btn').addEventListener('click', () => loadIncident(input.value));
    input.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') loadIncident(input.value);
    });

    $('#theme-toggle').addEventListener('click', () => {
        applyTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');
    });

    document.querySelectorAll('.tab').forEach((tab) => {
        tab.addEventListener('click', () => switchView(tab.dataset.view));
    });

    document.querySelectorAll('.graph-toolbar [data-action]').forEach((button) => {
        button.addEventListener('click', () => {
            if (!state.network) return;
            const scale = state.network.getScale();
            const actions = {
                'zoom-in': () => state.network.moveTo({ scale: scale * 1.25 }),
                'zoom-out': () => state.network.moveTo({ scale: scale / 1.25 }),
                fit: () => state.network.fit({ animation: { duration: 300 } }),
                relayout,
            };
            actions[button.dataset.action]?.();
        });
    });

    loadQueue();
    if (input.value.trim()) loadIncident(input.value);
});
