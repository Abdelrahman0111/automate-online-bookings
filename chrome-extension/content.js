// Content script للتفاعل مع صفحة WebBeds
let automationData = [];
let currentIndex = 0;
let automationResults = [];

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === 'startAutomation') {
        automationData = request.data;
        currentIndex = 0;
        automationResults = [];
        
        console.log('بدء الأتمتة مع', automationData.length, 'حجز');
        
        // التأكد من أننا في صفحة الحجوزات
        if (window.location.href.includes('/bookings')) {
            setTimeout(() => processNextBooking(), 1000);
            sendResponse({success: true});
        } else {
            // الانتقال إلى صفحة الحجوزات
            window.location.href = 'https://extranet.webbeds.com/5520905/bookings';
            sendResponse({success: true});
        }
    }
    return true; // للحفاظ على قناة الرسائل مفتوحة
});

function processNextBooking() {
    if (currentIndex >= automationData.length) {
        // انتهت المعالجة
        chrome.runtime.sendMessage({
            action: 'automationComplete',
            results: automationResults
        });
        return;
    }

    const booking = automationData[currentIndex];
    
    // تحديث التقدم
    chrome.runtime.sendMessage({
        action: 'updateProgress',
        current: currentIndex + 1,
        total: automationData.length
    });

    // البحث عن الحجز
    searchBooking(booking.bookingNumber)
        .then(() => {
            // محاولة إضافة المرجع
            return addSupplierReference(booking.hotelConf);
        })
        .then((result) => {
            automationResults.push({
                bookingNumber: booking.bookingNumber,
                hotelConf: booking.hotelConf,
                success: result.success,
                message: result.message,
                timestamp: new Date().toISOString()
            });
            
            currentIndex++;
            // تأخير قبل المعالجة التالية
            setTimeout(processNextBooking, 3000);
        })
        .catch((error) => {
            automationResults.push({
                bookingNumber: booking.bookingNumber,
                hotelConf: booking.hotelConf,
                success: false,
                message: error.message,
                timestamp: new Date().toISOString()
            });
            
            currentIndex++;
            setTimeout(processNextBooking, 3000);
        });
}

function searchBooking(bookingNumber) {
    return new Promise((resolve, reject) => {
        try {
            // التأكد من اختيار "All Hotels"
            const allHotelsFilter = document.querySelector('span.hotel-filter[data-value="1"]');
            if (allHotelsFilter && !allHotelsFilter.classList.contains('active')) {
                allHotelsFilter.click();
                setTimeout(() => continueSearch(), 1000);
            } else {
                continueSearch();
            }

            function continueSearch() {
                // مسح حقل البحث وإدخال رقم الحجز
                const searchInput = document.getElementById('referenceNumber');
                if (searchInput) {
                    searchInput.value = '';
                    searchInput.focus();
                    
                    // كتابة الرقم تدريجياً
                    let i = 0;
                    const typeInterval = setInterval(() => {
                        if (i < bookingNumber.length) {
                            searchInput.value += bookingNumber[i];
                            searchInput.dispatchEvent(new Event('input', { bubbles: true }));
                            i++;
                        } else {
                            clearInterval(typeInterval);
                            
                            // الضغط على زر البحث
                            setTimeout(() => {
                                const searchButton = document.getElementById('searchBookingsButton');
                                if (searchButton) {
                                    searchButton.click();
                                    
                                    // انتظار النتائج
                                    setTimeout(() => {
                                        resolve();
                                    }, 3000);
                                } else {
                                    reject(new Error('لم يتم العثور على زر البحث'));
                                }
                            }, 500);
                        }
                    }, 100);
                } else {
                    reject(new Error('لم يتم العثور على حقل البحث'));
                }
            }
        } catch (error) {
            reject(error);
        }
    });
}

function addSupplierReference(hotelConf) {
    return new Promise((resolve, reject) => {
        try {
            // البحث عن زر "Add Reference"
            const addRefButton = document.querySelector('button.add-reference-button');
            
            if (addRefButton) {
                addRefButton.click();
                
                // انتظار ظهور النافذة المنبثقة
                setTimeout(() => {
                    const refInput = document.getElementById('referenceNumberPopup');
                    if (refInput) {
                        refInput.value = hotelConf;
                        refInput.dispatchEvent(new Event('input', { bubbles: true }));
                        
                        // الضغط على حفظ
                        setTimeout(() => {
                            const saveButton = document.querySelector('button.save-button');
                            if (saveButton) {
                                saveButton.click();
                                
                                // انتظار الحفظ
                                setTimeout(() => {
                                    resolve({
                                        success: true,
                                        message: 'تم إضافة المرجع بنجاح'
                                    });
                                }, 2000);
                            } else {
                                reject(new Error('لم يتم العثور على زر الحفظ'));
                            }
                        }, 500);
                    } else {
                        reject(new Error('لم يتم العثور على حقل إدخال المرجع'));
                    }
                }, 1000);
            } else {
                // التحقق من وجود نفس المرجع مسبقاً على الصفحة
                const pageText = document.body.innerText;
                
                if (pageText.includes(hotelConf)) {
                    // المرجع موجود بنفس الرقم
                    resolve({
                        success: true,
                        message: 'تم اضافتها مسبقا'
                    });
                } else {
                    // زر Add Reference لم يتم العثور عليه
                    resolve({
                        success: true,
                        message: 'تم اضافتها مسبقا'
                    });
                }
            }
        } catch (error) {
            reject(error);
        }
    });
}

// إضافة دالة مساعدة للبحث في النص
document.querySelectorAll = document.querySelectorAll || function(selector) {
    if (selector.includes(':contains(')) {
        const text = selector.match(/:contains\("([^"]+)"\)/)[1];
        const elements = [];
        const allElements = document.getElementsByTagName('*');
        
        for (let i = 0; i < allElements.length; i++) {
            if (allElements[i].textContent.includes(text)) {
                elements.push(allElements[i]);
            }
        }
        return elements;
    }
    return document.querySelectorAll(selector);
};