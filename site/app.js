const files = ["research/projects.json","research/approaches.json","research/iterations.json","research/evidence.json"];
Promise.all(files.map(url => fetch(url).then(r => r.json()))).then(([projects, approaches, registry, evidence]) => render(projects, approaches, registry, evidence));

function render(projects, approaches, registry, evidence) {
  const project = document.querySelector("#project");
  projects.projects.forEach(p => project.add(new Option(p.name, p.id)));
  const state = document.querySelector("#state");
  const draw = () => {
    const selected = project.value;
    const filtered = registry.iterations.filter(i => (selected === "all" || i.project === selected) && (state.value === "all" || i.state === state.value));
    document.querySelector("#stats").innerHTML = [
      ["Iterations", filtered.length], ["Projects", new Set(filtered.map(i => i.project)).size],
      ["Evidence", evidence.records.filter(e => filtered.some(i => i.id === e.iteration)).length],
      ["Testing", filtered.filter(i => i.state === "testing").length], ["Archived", filtered.filter(i => i.state === "archived").length]
    ].map(([label,value]) => `<div class="stat"><span>${label}</span><strong>${value}</strong></div>`).join("");
    document.querySelector("#iterations").innerHTML = filtered.length ? filtered.map(i => {
      const p = projects.projects.find(x => x.id === i.project);
      const a = approaches.approaches.find(x => x.id === i.approach && x.version === i.approach_version);
      return `<article class="iteration"><span class="badge ${i.state}">${i.state}</span> <strong>${p.name} · iteration ${i.number}</strong><p>${a.name} <span class="meta">v${a.version} · ${i.scope}</span></p><p>${i.result}</p><span class="meta">Pinned commit <code>${i.commit}</code>${i.score === null ? " · score pending" : ` · score ${i.score}/32`}</span></article>`;
    }).join("") : "<p class=\"muted\">No iterations match this filter.</p>";
    document.querySelector("#approaches").innerHTML = approaches.approaches.map(a => `<p><span class="badge ${a.status === "archived" ? "archived" : ""}">${a.status}</span> <strong>${a.name}</strong> <span class="meta">v${a.version}</span><br>${a.definition}</p>`).join("");
    drawEvidence(filtered, evidence.records);
    drawGraph(filtered, evidence.records);
  };
  project.addEventListener("change", draw); state.addEventListener("change", draw); draw();
}
function drawEvidence(items, evidence) {
  const visible = evidence.filter(e => items.some(i => i.id === e.iteration));
  document.querySelector("#evidence").innerHTML = visible.length ? visible.map(e =>
    `<article class="evidence"><span class="badge ${e.status}">${e.status}</span> <strong>${e.id}</strong> <span class="meta">${e.kind} · confidence ${e.confidence}</span><p>${e.claim}</p><span class="meta">Source: <code>${e.source}</code></span></article>`
  ).join("") : "<p class=\"muted\">No evidence matches this filter.</p>";
}
function drawGraph(items, evidence) {
  const svg = document.querySelector("#graph"); const ns = "http://www.w3.org/2000/svg"; svg.replaceChildren();
  const positions = new Map(items.map((item, index) => [item.id, {x: 90 + (index % 4) * 245, y: 90 + Math.floor(index / 4) * 150}]));
  items.forEach(item => (item.relations || []).filter(relation => positions.has(relation.target) && item.id < relation.target).forEach(relation => {
  const id = relation.target;
  const a = positions.get(item.id), b = positions.get(id), line = document.createElementNS(ns,"line");
  line.setAttribute("x1",a.x); line.setAttribute("y1",a.y); line.setAttribute("x2",b.x); line.setAttribute("y2",b.y); line.setAttribute("class","edge"); svg.append(line);
  }));
  evidence.filter(e => positions.has(e.iteration)).forEach((e, index) => {
    const source = positions.get(e.iteration), p = {x: source.x, y: source.y + 68 + (index % 2) * 18};
    const line = document.createElementNS(ns, "line");
    line.setAttribute("x1", source.x); line.setAttribute("y1", source.y + 24); line.setAttribute("x2", p.x); line.setAttribute("y2", p.y - 7); line.setAttribute("class", "evidence-edge"); svg.append(line);
    const node = document.createElementNS(ns, "circle"); node.setAttribute("cx", p.x); node.setAttribute("cy", p.y); node.setAttribute("r", 7); node.setAttribute("class", "evidence-node"); svg.append(node);
    const label = document.createElementNS(ns, "text"); label.setAttribute("x", p.x + 12); label.setAttribute("y", p.y + 4); label.setAttribute("class", "evidence-label"); label.textContent = e.id; svg.append(label);
  });
  items.forEach(item => { const p=positions.get(item.id), c=document.createElementNS(ns,"circle"); c.setAttribute("cx",p.x); c.setAttribute("cy",p.y); c.setAttribute("r",24); c.setAttribute("class","node"); c.setAttribute("fill", item.state==="archived" ? "#94a3b8" : item.state==="collided" ? "#f59e0b" : "#60a5fa"); svg.append(c); const t=document.createElementNS(ns,"text"); t.setAttribute("x",p.x); t.setAttribute("y",p.y+45); t.setAttribute("text-anchor","middle"); t.setAttribute("class","node-label"); t.textContent=item.id; svg.append(t); });
}
