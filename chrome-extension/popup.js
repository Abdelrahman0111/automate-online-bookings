let processedData = null;
let automationResults = [];

document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    const processBtn = document.getElementById('processBtn');
    const startBtn = document.getElementById('startBtn');
    const status = document.getElementById('status');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');

    // رفع الملف
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#d32f2f';
    });
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = '#ccc';
    });
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#ccc';
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    processBtn.addEventListener('click', processFile);
    startBtn.addEventListener('click', startAutomation);

    function isValidNumber(value) {
        if (!value) return false;
        const str = String(value).trim();
        return str !== '' && !isNaN(str) && !isNaN(parseFloat(str));
    }

    function handleFile(file) {
        if (!file.name.match(/\.(xlsx|xls|csv)$/)) {
            showStatus('يرجى اختيار ملف Excel أو CSV صحيح', 'error');
            return;
        }

        fileName.textContent = file.name;
        fileInfo.style.display = 'block';
        processBtn.disabled = false;
        
        // حفظ الملف كـ base64 string
        const reader = new FileReader();
        reader.onload = function(e) {
            chrome.storage.local.set({
                'uploadedFile': {
                    name: file.name,
                    data: e.target.result.split(',')[1] // إزالة data:application/... prefix
                }
            });
        };
        reader.readAsDataURL(file);
    }

    function processFile() {
        showStatus('جاري تحليل الملف...', 'info');
        processBtn.disabled = true;

        chrome.storage.local.get(['uploadedFile'], function(result) {
            if (result.uploadedFile) {
                setTimeout(() => {
                    // تحديد نوع الملف
                    if (result.uploadedFile.name.endsWith('.csv')) {
                        parseCSVFile(result.uploadedFile.data);
                    } else {
                        parseExcelFile(result.uploadedFile.data);
                    }
                }, 1000);
            }
        });
    }

    function parseExcelFile(base64Data) {
        try {
            // تحويل base64 إلى ArrayBuffer
            const binaryString = atob(base64Data);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            
            // قراءة ملف Excel مباشرة
            const excelData = readExcelFile(bytes.buffer);
            
            console.log('بيانات Excel المقروءة:', excelData);
            
            // استخراج بيانات الحجوزات
            const bookingsData = [];
            
            excelData.forEach((row, index) => {
                const clientRef = row['ClientReference'] || row.ClientReference || '';
                const hotelConf = row['HotelConf'] || row.HotelConf || '';
                
                console.log(`السجل ${index + 1}:`, { clientRef, hotelConf });
                
                // التحقق من أن hotelConf يحتوي على أرقام فقط
                if (clientRef && isValidNumber(hotelConf)) {
                    bookingsData.push({
                        bookingNumber: clientRef.toString().trim(),
                        hotelConf: hotelConf.toString().trim()
                    });
                }
            });
            
            console.log('بيانات الحجوزات النهائية:', bookingsData);
            
            processedData = bookingsData;
            
            if (processedData && processedData.length > 0) {
                showStatus(`تم العثور على ${processedData.length} حجز جاهز للمعالجة`, 'success');
                startBtn.disabled = false;
            } else {
                showStatus('لم يتم العثور على بيانات صحيحة في الملف', 'error');
            }
            
            processBtn.disabled = false;
            
            // لا نرجع شيء هنا لأن المعالجة أصبحت غير متزامنة
        } catch (error) {
            console.error('خطأ في تحليل الملف:', error);
            showStatus('خطأ في تحليل ملف Excel: ' + error.message, 'error');
            processBtn.disabled = false;
        }
    }
    
    function parseCSVFile(base64Data) {
        try {
            // تحويل base64 إلى نص
            const csvText = atob(base64Data);
            
            console.log('CSV المقروء:', csvText);
            
            // تحليل CSV
            const lines = csvText.split('\n');
            const bookingsData = [];
            
            if (lines.length > 1) {
                const headers = lines[0].split(',');
                const clientRefIndex = headers.findIndex(h => h.includes('ClientReference'));
                const hotelConfIndex = headers.findIndex(h => h.includes('HotelConf'));
                
                console.log('مؤشرات الأعمدة:', { clientRefIndex, hotelConfIndex });
                
                for (let i = 1; i < lines.length; i++) {
                    const values = lines[i].split(',');
                    if (values.length > Math.max(clientRefIndex, hotelConfIndex)) {
                        const clientRef = values[clientRefIndex]?.trim();
                        const hotelConf = values[hotelConfIndex]?.trim();
                        
                        // التحقق من أن hotelConf يحتوي على أرقام فقط
                        if (clientRef && isValidNumber(hotelConf)) {
                            bookingsData.push({
                                bookingNumber: clientRef,
                                hotelConf: hotelConf
                            });
                        }
                    }
                }
            }
            
            console.log('بيانات CSV النهائية:', bookingsData);
            
            processedData = bookingsData;
            
            if (processedData && processedData.length > 0) {
                showStatus(`تم العثور على ${processedData.length} حجز جاهز للمعالجة`, 'success');
                startBtn.disabled = false;
            } else {
                showStatus('لم يتم العثور على بيانات صحيحة في الملف', 'error');
            }
            
            processBtn.disabled = false;
            
        } catch (error) {
            console.error('خطأ في تحليل CSV:', error);
            showStatus('خطأ في تحليل ملف CSV: ' + error.message, 'error');
            processBtn.disabled = false;
        }
    }

    function startAutomation() {
        if (!processedData || processedData.length === 0) {
            showStatus('لا توجد بيانات للمعالجة', 'error');
            return;
        }

        startBtn.disabled = true;
        document.getElementById('progressContainer').style.display = 'block';
        
        // إرسال البيانات إلى content script
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            if (tabs[0] && tabs[0].url && tabs[0].url.includes('extranet.webbeds.com')) {
                chrome.tabs.sendMessage(tabs[0].id, {
                    action: 'startAutomation',
                    data: processedData
                }, function(response) {
                    if (chrome.runtime.lastError) {
                        showStatus('خطأ في الاتصال: ' + chrome.runtime.lastError.message, 'error');
                        startBtn.disabled = false;
                        return;
                    }
                    if (response && response.success) {
                        showStatus('بدأت عملية الأتمتة...', 'info');
                    } else {
                        showStatus('خطأ في بدء الأتمتة', 'error');
                        startBtn.disabled = false;
                    }
                });
            } else {
                showStatus('يرجى الانتقال إلى صفحة WebBeds أولاً', 'error');
                startBtn.disabled = false;
            }
        });
    }

    function showStatus(message, type) {
        status.innerHTML = `<div class="status ${type}">${message}</div>`;
    }

    // استقبال النتائج من content script
    chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
        if (request.action === 'updateProgress') {
            const progress = (request.current / request.total) * 100;
            document.getElementById('progressBar').style.width = progress + '%';
            showStatus(`معالجة الحجز ${request.current} من ${request.total}`, 'info');
        } else if (request.action === 'automationComplete') {
            automationResults = request.results;
            showResults();
        }
    });

    function showResults() {
        const successCount = automationResults.filter(r => r.success).length;
        const failCount = automationResults.filter(r => !r.success).length;
        
        document.getElementById('successCount').textContent = successCount;
        document.getElementById('failCount').textContent = failCount;
        document.getElementById('results').style.display = 'block';
        document.getElementById('progressContainer').style.display = 'none';
        
        showStatus('تمت عملية الأتمتة بنجاح!', 'success');
        startBtn.disabled = false;
    }

    document.getElementById('downloadBtn').addEventListener('click', function() {
        const csvContent = generateCSVReport();
        downloadFile(csvContent, 'webbeds_automation_report.csv');
    });

    function generateCSVReport() {
        let csv = 'Booking Number,Hotel Conf,Status,Message,Timestamp\n';
        automationResults.forEach(result => {
            csv += `${result.bookingNumber},${result.hotelConf},${result.success ? 'Success' : 'Failed'},${result.message},${result.timestamp}\n`;
        });
        return csv;
    }

    function downloadFile(content, filename) {
        const blob = new Blob([content], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }
});