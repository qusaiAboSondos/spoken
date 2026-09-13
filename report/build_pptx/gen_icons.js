const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fs = require("fs");
const path = require("path");
const fa = require("react-icons/fa");

const OUT = path.join(__dirname, "icons");
fs.mkdirSync(OUT, { recursive: true });

// name -> [IconComponent, hexColor]
const icons = {
  mic: ["FaMicrophoneAlt"],
  shield: ["FaShieldAlt"],
  database: ["FaDatabase"],
  flask: ["FaFlask"],
  chart: ["FaChartBar"],
  warning: ["FaExclamationTriangle"],
  lightbulb: ["FaLightbulb"],
  play: ["FaPlayCircle"],
  check: ["FaCheckCircle"],
  users: ["FaUsers"],
  robot: ["FaRobot"],
  question: ["FaQuestionCircle"],
};

const color = process.argv[2] || "FFFFFF";

async function run() {
  for (const [name, [compName]] of Object.entries(icons)) {
    const Comp = fa[compName];
    const svgString = ReactDOMServer.renderToStaticMarkup(
      React.createElement(Comp, { size: 256, color: `#${color}` })
    );
    const fullSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 512 512">${svgString.match(/<path[^>]*>/g)?.join("") || ""}</svg>`;
    // react-icons FA components already output a full <svg>; just rasterize the rendered markup directly.
    const svgBuf = Buffer.from(svgString.startsWith("<svg") ? svgString : fullSvg);
    const outPath = path.join(OUT, `${name}_${color}.png`);
    await sharp(svgBuf).resize(256, 256).png().toFile(outPath);
    console.log("wrote", outPath);
  }
}
run();
