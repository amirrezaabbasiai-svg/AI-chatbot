class Chatbox {
    constructor() {
        this.studentId = typeof STUDENT_ID !== 'undefined' ? STUDENT_ID : 'anonymous_' + Date.now();
        this.openButton = document.querySelector('.chatbox__button button');
        this.chatBox = document.querySelector('.chatbox');
        this.sendButton = document.querySelector('.send__button');
        this.micButton = document.querySelector('.mic__button');
        this.messages = [];
        this.isWaiting = false;
        
        const saved = localStorage.getItem(`chat_${this.studentId}`);
        if (saved) {
            try {
                this.messages = JSON.parse(saved);
            } catch (e) {
                this.messages = [];
            }
        }
    }

    init() {
        if (!this.openButton || !this.chatBox) {
            console.error("❌ عناصر چت‌باکس پیدا نشدند!");
            return;
        }

        this.openButton.addEventListener('click', () => {
            this.chatBox.classList.toggle('chatbox--active');
        });

        this.sendButton.addEventListener('click', () => this.handleSend());
        const input = this.chatBox.querySelector('input');
        if (input) {
            input.addEventListener('keyup', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) this.handleSend();
            });
        }

        if (this.micButton) {
            this.initVoice();
        }

        this.renderMessages();
    }

    async handleSend() {
        if (this.isWaiting) return;

        const input = this.chatBox.querySelector('input');
        const text = input?.value.trim();
        if (!text) return;

        this.messages.push({ sender: 'user', text });
        this.saveHistory();
        this.renderMessages();
        input.value = '';

        this.messages.push({ sender: 'bot', text: 'در حال تایپ...' });
        this.renderMessages();
        this.isWaiting = true;

        try {
            const res = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await res.json();

            // حذف "در حال تایپ..." و شروع انیمیشن
            this.messages.pop();
            this.renderMessages();
            
            // انیمیشن تایپینگ هوشمند
            await this.typeMessage(data.response || 'پاسخی دریافت نشد.');
            
        } catch (err) {
            this.messages.pop();
            this.messages.push({ sender: 'bot', text: 'خطا در ارتباط با سرور.' });
            this.saveHistory();
            this.renderMessages();
        } finally {
            this.isWaiting = false;
        }
    }

    // انیمیشن تایپینگ هوشمند
    async typeMessage(fullMessage) {
        if (!fullMessage) {
            this.messages.push({ sender: 'bot', text: 'پاسخی دریافت نشد.' });
            this.saveHistory();
            this.renderMessages();
            return;
        }

        // تقسیم پیام به کلمات برای تایپ طبیعی‌تر
        const words = fullMessage.split(' ');
        let currentText = '';
        
        for (let i = 0; i < words.length; i++) {
            currentText += (i > 0 ? ' ' : '') + words[i];
            this.messages.push({ sender: 'bot', text: currentText });
            this.renderMessages();
            
            // تأخیر هوشمند: کلمات کوتاه‌تر سریع‌تر، بلندتر کندتر
            const wordLength = words[i].length;
            const delay = Math.min(100 + (wordLength * 15), 300);
            await new Promise(resolve => setTimeout(resolve, delay));
            
            // حذف پیام قبلی برای نمایش پیام کامل
            if (i < words.length - 1) {
                this.messages.pop();
            }
        }
        
        this.saveHistory();
    }

    saveHistory() {
        localStorage.setItem(`chat_${this.studentId}`, JSON.stringify(this.messages));
    }

    renderMessages() {
        const container = this.chatBox.querySelector('.chatbox__messages');
        if (!container) return;

        let html = '';
        this.messages.forEach((msg, index) => {
            const hasPersian = /[ا-ی]/.test(msg.text);
            const dirAttr = hasPersian ? 'dir="auto"' : '';
            
            if (msg.sender === 'bot') {
                html += `
                    <div class="messages__item messages__item--operator" ${dirAttr}>
                        <div class="message-content">${this.escape(msg.text)}</div>
                        <button class="voice-button" data-index="${index}">
                            <i class="fas fa-volume-up"></i>
                        </button>
                    </div>
                `;
            } else {
                html += `<div class="messages__item messages__item--visitor" ${dirAttr}>${this.escape(msg.text)}</div>`;
            }
        });

        container.innerHTML = html;
        container.scrollTop = container.scrollHeight;

        container.querySelectorAll('.voice-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const index = parseInt(e.target.closest('.voice-button').dataset.index);
                const text = this.messages[index].text;
                this.speakMessage(text);
            });
        });
    }

    initVoice() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.log("مرورگر از SpeechRecognition پشتیبانی نمی‌کنه");
            if (this.micButton) {
                this.micButton.style.display = 'none';
            }
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'fa-IR';

        if (this.micButton) {
            this.micButton.addEventListener('click', () => {
                if (this.isWaiting) return;
                this.micButton.classList.add('recording');
                recognition.start();
            });
        }

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.micButton.classList.remove('recording');
            const input = this.chatBox.querySelector('input');
            if (input) {
                input.value = transcript;
                this.handleSend();
            }
        };

        recognition.onerror = (event) => {
            this.micButton.classList.remove('recording');
            console.error("خطا در ضبط صدا:", event.error);
            if (event.error === 'not-allowed') {
                alert("لطفاً مجوز دسترسی به میکروفون را فعال کنید.");
            }
        };
    }

    async speakMessage(text) {
        if (!text || !text.trim()) return;
        
        // نمایش انیمیشن در حال پخش
        const voiceButtons = document.querySelectorAll('.voice-button');
        voiceButtons.forEach(btn => {
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        });
        
        try {
            const response = await fetch('/speak', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            });
            
            if (response.ok) {
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                audio.play();
                
                // بازگرداندن آیکون اصلی بعد از پخش
                audio.onended = () => {
                    URL.revokeObjectURL(audioUrl);
                    this.restoreVoiceButtons();
                };
                audio.onerror = () => {
                    URL.revokeObjectURL(audioUrl);
                    this.restoreVoiceButtons();
                };
            } else {
                throw new Error('خطا در تولید صدا');
            }
        } catch (error) {
            console.error('خطا در پخش صدا:', error);
            this.restoreVoiceButtons();
        }
    }

    restoreVoiceButtons() {
        const voiceButtons = document.querySelectorAll('.voice-button');
        voiceButtons.forEach(btn => {
            btn.innerHTML = '<i class="fas fa-volume-up"></i>';
        });
    }

    escape(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new Chatbox().init();
});