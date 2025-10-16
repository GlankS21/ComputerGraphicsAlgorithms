// изображение (исходное и варианты).
let orig = document.getElementsByTagName("canvas").item(0);
let bright = document.getElementsByTagName("canvas").item(2);
let cont = document.getElementsByTagName("canvas").item(4);
let inverted = document.getElementsByTagName("canvas").item(6);

// для рисования соответствующей гистограммы.
let histOrig = document.getElementsByTagName("canvas").item(1);
let histBright = document.getElementsByTagName("canvas").item(3);
let histCont = document.getElementsByTagName("canvas").item(5);
let histInverted = document.getElementsByTagName("canvas").item(7);

// диапазон ввода
let brightSlider = document.getElementById("brightness");
let contrastSlider = document.getElementById("contrast");
let invertedSlider = document.getElementById("inverted");
// источник изображения
let upload = document.getElementById("upload");

// Создание нового изображения
let imageGlobal = new Image();

// значения цветовых каналов находятся в пределах [0,255]
function clamp(v) {
  if (v < 0) return 0;
  if (v > 255) return 255;
  return v;
}

// преобразовать значение в целое число
function safeInt(v) {
  return Math.round(Number(v) || 0);
}

// Установка обработчика события "onload" для окна браузера
window.onload = async () => {
  let canvases = document.getElementsByTagName("canvas"); 
  // Установить размер
  for (let i = 0; i < canvases.length; i++) {  
    let canvas = canvases.item(i);
    let bounds = canvas.getBoundingClientRect();
    canvas.width = bounds.width || canvas.width || 300;
    canvas.height = bounds.height || canvas.height || 150;
  }

  // khởi tạo slider mặc định
  brightSlider.value = 50; 
  contrastSlider.value = 0; 
  invertedSlider.value = 50;

  // Загружаем дефолтное изображение (если есть)
  await uploadImage("./cat.webp");

  // метки ползунка и значения гистограммы.
  updateSliderLabelAttrs();
};

// Обработка изменений пользователем ползунков
brightSlider.oninput = () => {
  updateSliderLabelAttrs();
  calculate(orig, bright, histBright, (brightSlider.value / 50 - 1), "brightness");
};

contrastSlider.oninput = () => {
  updateSliderLabelAttrs();
  calculate(orig, cont, histCont, contrastSlider.value, "contrast");
};

invertedSlider.oninput = () => {
  updateSliderLabelAttrs();
  calculate(orig, inverted, histInverted, invertedSlider.value / 100, "inverted");
};

// title и aria-valuenow
function updateSliderLabelAttrs() {
  brightSlider.setAttribute("title", `Brightness: ${brightSlider.value}`);
  brightSlider.setAttribute("aria-valuenow", brightSlider.value);

  contrastSlider.setAttribute("title", `Contrast: ${contrastSlider.value}`);
  contrastSlider.setAttribute("aria-valuenow", contrastSlider.value);

  invertedSlider.setAttribute("title", `Inverted: ${invertedSlider.value}`);
  invertedSlider.setAttribute("aria-valuenow", invertedSlider.value);
}

// Функция для чтения изображения в формате Data URL
function readAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const fr = new FileReader();
    fr.onerror = reject;
    fr.onload = () => resolve(fr.result);
    fr.readAsDataURL(file);
  });
}

// Функция вычисления
async function calculate(origCanvas, canvas, histCanvas, value, type) {
  let ctx = canvas.getContext("2d");
  let ctxOrig = origCanvas.getContext("2d");

  const w = origCanvas.width;
  const h = origCanvas.height;
  if (w === 0 || h === 0) return;

  let imageData = ctxOrig.getImageData(0, 0, w, h);
  let data = imageData.data;

  if (type === "contrast") {
    let contrast = value * (255 / 100);
    let factor = (255 + contrast) / (255.01 - contrast);
    for (let i = 0; i < data.length; i += 4) {
      data[i] = clamp(Math.round(factor * (data[i] - 128) + 128));
      data[i + 1] = clamp(Math.round(factor * (data[i + 1] - 128) + 128));
      data[i + 2] = clamp(Math.round(factor * (data[i + 2] - 128) + 128));
    }
  } 
  else if (type === "brightness") {
    let factor = 1 + value; // value từ -0.5..+0.5
    for (let i = 0; i < data.length; i += 4) {
      data[i] = clamp(Math.round(data[i] * factor));
      data[i + 1] = clamp(Math.round(data[i + 1] * factor));
      data[i + 2] = clamp(Math.round(data[i + 2] * factor));
    }
  } 
  else if (type === "inverted") {
    for (let i = 0; i < data.length; i += 4) {
      data[i] = clamp(Math.round(255 - data[i] * value));
      data[i + 1] = clamp(Math.round(255 - data[i + 1] * value));
      data[i + 2] = clamp(Math.round(255 - data[i + 2] * value));
    }
  }

  ctx.putImageData(imageData, 0, 0);
  processImage(ctx.getImageData(0, 0, canvas.width, canvas.height).data, histCanvas, type);
}

// Обновленный processImage с label
function processImage(data, histCanvas, type) {
  let histR = new Array(256).fill(0);
  let histG = new Array(256).fill(0);
  let histB = new Array(256).fill(0);

  for (let i = 0; i < data.length; i += 4) {
    histR[data[i]]++;
    histG[data[i + 1]]++;
    histB[data[i + 2]]++;
  }

  let maxBrightness = Math.max(...histR, ...histG, ...histB, 1);

  const ctx = histCanvas.getContext("2d");
  let dx = histCanvas.width / 256;
  let dy = histCanvas.height / maxBrightness;
  ctx.fillStyle = "#fff";
  ctx.fillRect(0, 0, histCanvas.width, histCanvas.height);
  ctx.lineWidth = Math.max(1, Math.floor(dx));

  for (let i = 0; i < 256; i++) {
    let x = i * dx + dx / 2;

    ctx.strokeStyle = "rgba(255,0,0,0.55)";
    ctx.beginPath();
    ctx.moveTo(x, histCanvas.height);
    ctx.lineTo(x, histCanvas.height - histR[i] * dy);
    ctx.stroke();

    ctx.strokeStyle = "rgba(0,255,0,0.55)";
    ctx.beginPath();
    ctx.moveTo(x, histCanvas.height);
    ctx.lineTo(x, histCanvas.height - histG[i] * dy);
    ctx.stroke();

    ctx.strokeStyle = "rgba(0,0,255,0.55)";
    ctx.beginPath();
    ctx.moveTo(x, histCanvas.height);
    ctx.lineTo(x, histCanvas.height - histB[i] * dy);
    ctx.stroke();
  }

  ctx.font = "12px Arial";
  ctx.textBaseline = "top";
  const padding = 6;
  const gap = 28;
  ctx.fillStyle = "red";
  ctx.fillRect(padding, padding, 12, 12);
  ctx.fillStyle = "#000";
  ctx.fillText("R", padding + 16, padding);
  ctx.fillStyle = "green";
  ctx.fillRect(padding + gap, padding, 12, 12);
  ctx.fillStyle = "#000";
  ctx.fillText("G", padding + gap + 16, padding);
  ctx.fillStyle = "blue";
  ctx.fillRect(padding + gap * 2, padding, 12, 12);
  ctx.fillStyle = "#000";
  ctx.fillText("B", padding + gap * 2 + 16, padding);

  // label
  let textLabel = "Original";
  if (type === "brightness") textLabel = `Brightness: ${safeInt(brightSlider.value)}%`;
  if (type === "contrast") textLabel = `Contrast: ${safeInt(contrastSlider.value)}`;
  if (type === "inverted") textLabel = `Inverted: ${safeInt(invertedSlider.value)}%`;

  ctx.save();
  ctx.font = "12px Arial";
  ctx.textBaseline = "top";
  const metrics = ctx.measureText(textLabel);
  const textW = metrics.width;
  const textH = 14;
  const x = histCanvas.width - textW - padding;
  const y = padding;

  ctx.fillStyle = "rgba(255,255,255,0.8)";
  ctx.fillRect(x - 4, y - 2, textW + 8, textH + 4);
  ctx.fillStyle = "#000";
  ctx.fillText(textLabel, x, y);
  ctx.restore();
}

async function uploadImage(image) {
  let img = new Image();
  if (image instanceof File) {
    const url = await readAsDataURL(image);
    img.src = url;
  } else img.src = image;
  await img.decode();

  imageGlobal.src = img.src;
  loadImage(img, orig, histOrig);
  calculate(orig, bright, histBright, (brightSlider.value / 50 - 1), "brightness");
  calculate(orig, cont, histCont, contrastSlider.value, "contrast");
  calculate(orig, inverted, histInverted, invertedSlider.value / 100, "inverted");
}

// tải và hiển thị ảnh lên canvas, đồng thời tính và vẽ histogram tương ứng
function loadImage(img, canvas, histCanvas) {
  let ctx = canvas.getContext("2d");
  drawImageProp(ctx, img, 0, 0, canvas.width, canvas.height);
  processImage(ctx.getImageData(0, 0, canvas.width, canvas.height).data, histCanvas);
}

// hiển thị ảnh trên canvas vừa khít, không méo tỉ lệ, và có thể chọn vùng trung tâm/offset để hiển thị
function drawImageProp(ctx, img, x, y, w, h, offsetX, offsetY) {
  if (arguments.length === 2) {
    x = y = 0;
    w = ctx.canvas.width;
    h = ctx.canvas.height;
  }
  offsetX = typeof offsetX === "number" ? offsetX : 0.5;
  offsetY = typeof offsetY === "number" ? offsetY : 0.5;
  if (offsetX < 0) offsetX = 0;
  if (offsetY < 0) offsetY = 0;
  if (offsetX > 1) offsetX = 1;
  if (offsetY > 1) offsetY = 1;

  var iw = img.width,
    ih = img.height,
    r = Math.min(w / iw, h / ih),
    nw = iw * r,
    nh = ih * r,
    ar = 1;

  if (nw < w) ar = w / nw;
  if (Math.abs(ar - 1) < 1e-14 && nh < h) ar = h / nh;
  nw *= ar;
  nh *= ar;
  var cw = iw / (nw / w);
  var ch = ih / (nh / h);
  var cx = (iw - cw) * offsetX;
  var cy = (ih - ch) * offsetY;

  if (cx < 0) cx = 0;
  if (cy < 0) cy = 0;
  if (cw > iw) cw = iw;
  if (ch > ih) ch = ih;

  ctx.drawImage(img, cx, cy, cw, ch, x, y, w, h);
}
