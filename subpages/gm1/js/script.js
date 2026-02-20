const inputText = document.getElementById('inputText');
const convertToUnicodeButton = document.getElementById('convertToUnicode');
const unicodeInput = document.getElementById('unicodeInput');
const numberInput = document.getElementById('numberInput');
const applyNumbersButton = document.getElementById('applyNumbers');
const resultDiv = document.getElementById('result');

convertToUnicodeButton.addEventListener('click', () => {
  const text = inputText.value;
  let unicode = '';
  for (let i = 0; i < text.length; i++) {
    unicode += text.charCodeAt(i) + ' ';
  }
  unicodeInput.value = unicode.trim();
});

applyNumbersButton.addEventListener('click', () => {
  const unicodeStr = unicodeInput.value;
  const numbersStr = numberInput.value;

  if (!unicodeStr || !numbersStr) {
    resultDiv.textContent = '请先输入文本和数字。';
    return;
  }

  const unicodeArr = unicodeStr.split(' ').map(Number);
  const numbersArr = numbersStr.split(',').map(Number);

  let resultUnicodeArr = [];
  for (let i = 0; i < unicodeArr.length; i++) {
    const numToAdd = numbersArr[i % numbersArr.length];
    resultUnicodeArr.push(unicodeArr[i] + numToAdd);
  }

  let resultText = '';
  for (let i = 0; i < resultUnicodeArr.length; i++) {
    resultText += String.fromCharCode(resultUnicodeArr[i]);
  }

  resultDiv.textContent = '结果：' + resultText;
});