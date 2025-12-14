// Background script للتعامل مع الأحداث
chrome.runtime.onInstalled.addListener(() => {
    console.log('WebBeds Automation Extension installed');
});

// التعامل مع الرسائل بين المكونات
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'updateProgress') {
        // إعادة توجيه رسالة التقدم إلى popup
        chrome.runtime.sendMessage(request);
    } else if (request.action === 'automationComplete') {
        // إعادة توجيه رسالة اكتمال الأتمتة إلى popup
        chrome.runtime.sendMessage(request);
    }
});

// التعامل مع تحديث التبويبات
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.includes('extranet.webbeds.com')) {
        // تفعيل الإضافة عند تحميل صفحة WebBeds
        chrome.action.setBadgeText({
            text: '✓',
            tabId: tabId
        });
        chrome.action.setBadgeBackgroundColor({
            color: '#4CAF50',
            tabId: tabId
        });
    }
});