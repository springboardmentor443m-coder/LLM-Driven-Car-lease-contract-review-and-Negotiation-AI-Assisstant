import React, { useRef, useState } from 'react';
import { Upload, File } from 'lucide-react';

const FileUpload = ({ onFileSelect }) => {
    const fileInputRef = useRef(null);
    const [isDragging, setIsDragging] = useState(false);

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            onFileSelect(files[0]);
        }
    };

    const handleClick = () => {
        fileInputRef.current.click();
    };

    const handleInputChange = (e) => {
        if (e.target.files && e.target.files.length > 0) {
            onFileSelect(e.target.files[0]);
        }
    };

    return (
        <div 
            onClick={handleClick}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            style={{
                border: `2px dashed ${isDragging ? '#10b981' : '#4b5563'}`, // Emerald vs Gray border
                backgroundColor: isDragging ? 'rgba(16, 185, 129, 0.1)' : 'var(--bg-card)',
                borderRadius: '16px',
                padding: '40px',
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                position: 'relative'
            }}
        >
            <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleInputChange} 
                style={{ display: 'none' }} 
                accept=".pdf,.png,.jpg,.jpeg"
            />
            
            <div style={{
                width: '64px', height: '64px', 
                backgroundColor: 'var(--bg-dark)', 
                borderRadius: '50%', 
                display: 'flex', alignItems: 'center', justifyContent: 'center', 
                margin: '0 auto 16px auto',
                boxShadow: '0 4px 6px rgba(0,0,0,0.3)'
            }}>
                {isDragging ? (
                    <File size={32} color="#10b981" />
                ) : (
                    <Upload size={32} color="#10b981" />
                )}
            </div>

            <h3 style={{ color: 'white', margin: '0 0 8px 0', fontSize: '1.1rem' }}>
                {isDragging ? "Drop file here" : "Click to Upload Contract"}
            </h3>
            <p style={{ color: '#9ca3af', fontSize: '0.9rem', margin: 0 }}>
                Supports PDF, PNG, JPG (Max 10MB)
            </p>
        </div>
    );
};

export default FileUpload;