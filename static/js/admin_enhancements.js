// Zonuko Admin Enhancements - Phase 2

document.addEventListener('DOMContentLoaded', function() {
    // Add emoji picker to emoji field
    addEmojiPicker();
    
    // Enhance file upload fields
    enhanceFileUploads();
});

function addEmojiPicker() {
    const emojiField = document.querySelector('#id_emoji');
    if (!emojiField) return;
    
    // Popular emojis for STEAM projects
    const popularEmojis = [
        '🚀', '🔬', '🎨', '🧪', '🔭', '🌟',
        '💡', '🎭', '🎪', '🎬', '📸', '🎵',
        '🎹', '🎸', '🥁', '🎤', '🎧', '📻',
        '🌈', '⚡', '🔥', '💧', '🌊', '🌍',
        '🌙', '⭐', '☀️', '🌤️', '⛅', '🌈',
        '🦋', '🐝', '🐛', '🌺', '🌻', '🌼',
        '🍎', '🥕', '🌽', '🥦', '🍕', '🍰',
        '⚙️', '🔧', '🔩', '⚡', '🔋', '💻',
        '🤖', '👾', '🎮', '🎲', '🧩', '🎯',
        '🏆', '🥇', '🎖️', '⭐', '✨', '💫'
    ];
    
    // Create emoji picker button
    const pickerBtn = document.createElement('button');
    pickerBtn.type = 'button';
    pickerBtn.className = 'emoji-picker-btn';
    pickerBtn.innerHTML = '😀';
    pickerBtn.title = 'Pick an emoji';
    
    // Create emoji picker popup
    const popup = document.createElement('div');
    popup.className = 'emoji-picker-popup';
    
    const grid = document.createElement('div');
    grid.className = 'emoji-grid';
    
    popularEmojis.forEach(emoji => {
        const item = document.createElement('span');
        item.className = 'emoji-item';
        item.textContent = emoji;
        item.title = emoji;
        item.addEventListener('click', () => {
            emojiField.value = emoji;
            popup.classList.remove('show');
        });
        grid.appendChild(item);
    });
    
    popup.appendChild(grid);
    
    // Insert after the emoji field
    emojiField.parentNode.appendChild(pickerBtn);
    emojiField.parentNode.appendChild(popup);
    
    // Toggle popup
    pickerBtn.addEventListener('click', (e) => {
        e.preventDefault();
        popup.classList.toggle('show');
    });
    
    // Close popup when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.emoji-picker-btn') && !e.target.closest('.emoji-picker-popup')) {
            popup.classList.remove('show');
        }
    });
}

function enhanceFileUploads() {
    // Add visual feedback for file uploads
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        // Show current file if exists
        const currentFile = input.parentNode.querySelector('a');
        if (currentFile && currentFile.href) {
            const status = document.createElement('span');
            status.className = 'file-status';
            status.textContent = '✓ File uploaded';
            currentFile.parentNode.insertBefore(status, currentFile.nextSibling);
        }
        
        // Add change event listener
        input.addEventListener('change', (e) => {
            const fileName = e.target.files[0]?.name;
            if (fileName) {
                // Remove old status if exists
                const oldStatus = input.parentNode.querySelector('.file-status');
                if (oldStatus) oldStatus.remove();
                
                // Add new status
                const status = document.createElement('span');
                status.className = 'file-status';
                status.style.background = '#667eea';
                status.textContent = `📎 ${fileName}`;
                input.parentNode.appendChild(status);
            }
        });
    });
}

// Add helpful tooltips for video upload
const videoFileField = document.querySelector('#id_video_file');
const videoUrlField = document.querySelector('#id_video_url');

if (videoFileField && videoUrlField) {
    // Disable one when the other is filled
    videoFileField.addEventListener('change', () => {
        if (videoFileField.files.length > 0) {
            videoUrlField.disabled = true;
            videoUrlField.style.opacity = '0.5';
        } else {
            videoUrlField.disabled = false;
            videoUrlField.style.opacity = '1';
        }
    });
    
    videoUrlField.addEventListener('input', () => {
        if (videoUrlField.value) {
            videoFileField.disabled = true;
            videoFileField.style.opacity = '0.5';
        } else {
            videoFileField.disabled = false;
            videoFileField.style.opacity = '1';
        }
    });
}
