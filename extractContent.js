const fs = require("fs");
const path = require("path");

const OUTPUT_FILE = "Proyecto_Actualizado.txt"; // Archivo de salida
const MAX_LINES = 100000; // Máximo de líneas a incluir por archivo

/**
 * Recorrer el directorio y obtener la estructura y contenido.
 * @param {string} dirPath - Ruta del directorio a recorrer
 * @param {string} relativePath - Ruta relativa para mostrar
 * @param {Array} result - Resultado acumulado
 */
function readDirectory(dirPath, relativePath = "", result = []) {
  const files = fs.readdirSync(dirPath);

  // Define ignored patterns (moved outside the loop for better readability)
  const ignoredPatterns = [
    ".pycache__",
    ".pytest_cache__",
    "customer_acquisition.db",
    "extractContent.js",
    "docs",
    "node_modules",
    "env",
    ".next",
    "package-lock.json",
    "package.json",
    "tailwind.config.js",
    "tsconfig.json",
    "next.config.js",
    "postcss.config.js",
    "next-env.d.ts",
    "yarn.lock",
    "next-env.d.ts",
    "__pycache__",
    "auth_info_baileys",
  ];

  files.forEach((file) => {
    const fullPath = path.join(dirPath, file);
    const relativeFilePath = path.join(relativePath, file);
    const stats = fs.statSync(fullPath);

    // Check if the current file/directory should be ignored
    if (ignoredPatterns.some(pattern => 
      relativeFilePath.includes(pattern) || 
      file === pattern || 
      file === pattern + "/"
    )) {
      return; // Skip this file/directory and its contents
    }

    // Ignorar archivos de imagen
    const imageExtensions = [".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg"];
    if (stats.isFile() && imageExtensions.includes(path.extname(file).toLowerCase())) {
      return; // Ignorar si el archivo es una imagen
    }

    if (stats.isDirectory()) {
      // Si es un directorio, añadirlo y recorrerlo
      result.push({ type: "directory", path: relativeFilePath });
      readDirectory(fullPath, relativeFilePath, result);
    } else if (stats.isFile()) {
      // Si es un archivo, leer el contenido
      const content = fs
        .readFileSync(fullPath, "utf-8")
        .split("\n")
        .slice(0, MAX_LINES)
        .join("\n");
      result.push({ type: "file", path: relativeFilePath, content });
    }
  });

  return result;
}

/**
 * Guardar la estructura del proyecto en un archivo.
 * @param {Array} structure - Estructura del proyecto
 */
function saveToFile(structure) {
  const output = structure
    .map((item) => {
      if (item.type === "directory") {
        return `📂 ${item.path}/`;
      } else if (item.type === "file") {
        return `📄 ${item.path}\n---\n${item.content}\n---`;
      }
    })
    .join("\n\n");

  fs.writeFileSync(OUTPUT_FILE, output, "utf-8");
  console.log(`Estructura del proyecto guardada en: ${OUTPUT_FILE}`);
}

// Punto de entrada
const projectDir = path.resolve(__dirname); // Cambiar si necesitas recorrer otro directorio
const structure = readDirectory(projectDir);
saveToFile(structure);
