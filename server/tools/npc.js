var WORKSPACE = require('../workspace.js');

function placeNPC(workspace, body) {
  let key = body.key;
  if (!key) {
    console.log("[placeNPC] invalid key");
    return false;
  }

  let npcs = WORKSPACE.readNPCs(workspace);

  wanderArea = {
    "type": body.wander,
  };
  if (wanderArea.type == "circle") {
    wanderArea.radius = body.w;
    wanderArea.x = body.gx;
    wanderArea.y = body.gy;
  } else if (wanderArea.type == "rect") {
    wanderArea.minx = body.gx;
    wanderArea.miny = body.gy;
    wanderArea.maxx = body.gx + body.w;
    wanderArea.maxy = body.gy + body.h;
  } else {
    console.log("[placeNPC] invalid wander type: " + wanderArea.type);
    return false;
  }

  npcs[key] = {
    "npc": body.npc,
    "capacity": body.count,
    "wanderArea": wanderArea,
    "spawnLocations": [],
  }

  WORKSPACE.writeNPCs(workspace, npcs);
  return true;
}

function placeSpawn(workspace, body) {
  let key = body.key;
  if (!key) {
    console.log("[placeNPC] invalid key: " + key);
    return false;
  }

  let npcs = WORKSPACE.readNPCs(workspace);
  let npc = npcs[key];
  if (!npc) {
    console.log("no such npc: " + key);
    return false;
  }

  let gx = body.gx;
  let gy = body.gy;
  if (!gx || !gy) {
    return false;
  }

  let wander = npc.wanderArea;
  if (wander.type == "circle" && (
    true // TODO
  )) {
    console.log("TODO: place in circle");
    return false;
  }
  if (wander.type == "rect" && (
    gx < wander.minx ||
    gy < wander.miny ||
    gx >= wander.maxx ||
    gy >= wander.maxy
  )) {
    console.log("out of bounds placement");
    return false;
  }

  npcs[key]["spawnLocations"].push({ "x": gx, "y": gy });
  WORKSPACE.writeNPCs(workspace, npcs);
  return true;
}

exports.init = (app) => {
  app.post('/place/:workspace', (req, res) => {
    res.send(placeNPC(req.params.workspace, req.body));
  });
  app.post('/placeSpawn/:workspace', (req, res) => {
    res.send(placeSpawn(req.params.workspace, req.body));
  });
  return app;
}
