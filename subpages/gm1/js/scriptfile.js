// const htmlFileInput = document.getElementById('htmlFileInput');
// const numberInput = document.getElementById('numberInput');
// const encryptHTMLButton = document.getElementById('encryptHTML');
// const downloadLink = document.getElementById('downloadLink');

// encryptHTMLButton.addEventListener('click', () => {
//   const htmlFile = htmlFileInput.files[0];
//   const numbersStr = numberInput.value;

//   if (!htmlFile || !numbersStr) {
//     alert('请选择 HTML 文件和输入数字密钥。');
//     return;
//   }

//   const htmlReader = new FileReader();

//   htmlReader.onload = (htmlEvent) => {
//     const htmlStr = htmlEvent.target.result;
//     const numbersArr = numbersStr.split(',').map(Number);

//     const parser = new DOMParser();
//     const doc = parser.parseFromString(htmlStr, 'text/html');
//     const encryptElements = doc.querySelectorAll('.Encryptu');

//     encryptElements.forEach((element) => {
//       const text = element.textContent;
//       let unicodeArr = [];
//       for (let i = 0; i < text.length; i++) {
//         unicodeArr.push(text.charCodeAt(i));
//       }

//       let resultUnicodeArr = [];
//       for (let i = 0; i < unicodeArr.length; i++) {
//         const numToAdd = numbersArr[i % numbersArr.length];
//         resultUnicodeArr.push(unicodeArr[i] + numToAdd);
//       }

//       let resultText = '';
//       for (let i = 0; i < resultUnicodeArr.length; i++) {
//         resultText += String.fromCharCode(resultUnicodeArr[i]);
//       }

//       element.textContent = resultText;
//       element.classList.remove('Encryptu');
//       element.classList.add('Encryptedu');
//     });

//     const resultHTML = doc.documentElement.outerHTML;
//     const blob = new Blob([resultHTML], { type: 'text/html' });
//     const url = URL.createObjectURL(blob);

//     downloadLink.href = url;
//     downloadLink.download = 'encrypted.html';
//     downloadLink.style.display = 'block';
//   };

//   htmlReader.readAsText(htmlFile);
// });
const htmlFileInput = document.getElementById('htmlFileInput');
const numberInput = document.getElementById('numberInput');
const encryptHTMLButton = document.getElementById('encryptHTML');
const downloadLink = document.getElementById('downloadLink');

encryptHTMLButton.addEventListener('click', () => {
  const htmlFile = htmlFileInput.files[0];
  const numbersStr = numberInput.value;

  if (!htmlFile || !numbersStr) {
    alert('请选择 HTML 文件和输入数字密钥。');
    return;
  }

  const htmlReader = new FileReader();

  htmlReader.onload = (htmlEvent) => {
    let htmlStr = htmlEvent.target.result;
    const numbersArr = numbersStr.split(',').map(Number);

    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlStr, 'text/html');
    const encryptElements = doc.querySelectorAll('.Encryptu');

    encryptElements.forEach((element) => {
      let originalHTML = element.innerHTML;
      let text = originalHTML.replace(/<[^>]*>/g, (match, index) => {
        return `\u0000${index}\u0000`; // 使用特殊字符作为占位符
      });

      let tagMap = {};
      let tagIndex = 0;
      originalHTML.replace(/<[^>]*>/g, (match) => {
        tagMap[`\u0000${tagIndex}\u0000`] = match;
        tagIndex++;
      });

      let unicodeArr = [];
      for (let i = 0; i < text.length; i++) {
        unicodeArr.push(text.charCodeAt(i));
      }

      let resultUnicodeArr = [];
      for (let i = 0; i < unicodeArr.length; i++) {
        const numToAdd = numbersArr[i % numbersArr.length];
        resultUnicodeArr.push(unicodeArr[i] + numToAdd);
      }

      let resultText = '';
      for (let i = 0; i < resultUnicodeArr.length; i++) {
        resultText += String.fromCharCode(resultUnicodeArr[i]);
      }

      // 恢复原始标签
      Object.keys(tagMap).forEach((key) => {
        resultText = resultText.replace(key, tagMap[key]);
      });

      element.innerHTML = resultText;
      element.classList.remove('Encryptu');
      element.classList.add('Encryptedu');
    });

    const resultHTML = doc.documentElement.outerHTML;
    const blob = new Blob([resultHTML], { type: 'text/html' });
    const url = URL.createObjectURL(blob);

    downloadLink.href = url;
    downloadLink.download = 'encrypted.html';
    downloadLink.style.display = 'block';
  };

  htmlReader.readAsText(htmlFile);
});