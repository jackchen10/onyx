import { useState, useEffect, useRef, useCallback } from 'react';

interface UseSpeechRecognitionReturn {
    isListening: boolean;
    transcript: string;
    startListening: () => void;
    stopListening: () => void;
    resetTranscript: () => void;
    hasRecognitionSupport: boolean;
    error: string | null;
}

export const useSpeechRecognition = (): UseSpeechRecognitionReturn => {
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [hasSupport, setHasSupport] = useState(false);
    const recognitionRef = useRef<any>(null);

    useEffect(() => {
        if (typeof window !== 'undefined') {
            const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
            if (SpeechRecognition) {
                setHasSupport(true);
                const recognition = new SpeechRecognition();
                recognition.continuous = true;
                recognition.interimResults = true;
                recognition.lang = 'zh-CN';

                recognition.onresult = (event: any) => {
                    let finalTranscript = '';
                    let interimTranscript = '';

                    for (let i = event.resultIndex; i < event.results.length; i++) {
                        const transcript = event.results[i][0].transcript;
                        if (event.results[i].isFinal) {
                            finalTranscript += transcript;
                        } else {
                            interimTranscript += transcript;
                        }
                    }
                    // 实时更新,由组件决定如何使用
                    setTranscript(finalTranscript || interimTranscript);
                };

                recognition.onerror = (event: any) => {
                    console.warn('Speech recognition error:', event.error);
                    // 忽略一些非致命错误
                    if (event.error === 'no-speech') return;
                    setError(event.error);
                    setIsListening(false);
                };

                recognition.onend = () => {
                    setIsListening(false);
                };

                recognitionRef.current = recognition;
            }
        }
    }, []);

    const startListening = useCallback(() => {
        if (!recognitionRef.current || !hasSupport) {
            console.warn('[VoiceInput] Recognition not supported or not initialized');
            return;
        }
        try {
            console.log('[VoiceInput] Attempting to start speech recognition...');
            setError(null);
            setTranscript('');
            recognitionRef.current.start();
            // 只有成功调用 start() 后才设置为 true
            // 如果权限被拒，start() 会立即触发 onerror，isListening 会在那里被设为 false
            setIsListening(true);
            console.log('[VoiceInput] Speech recognition started successfully');
        } catch (err: any) {
            console.error('[VoiceInput] Failed to start recognition:', err);
            console.error('[VoiceInput] Error details:', {
                name: err?.name,
                message: err?.message,
                stack: err?.stack
            });
            setError(err?.message || 'Failed to start');
            setIsListening(false);
        }
    }, [hasSupport]);

    const stopListening = useCallback(() => {
        if (!recognitionRef.current) return;
        try {
            recognitionRef.current.stop();
            setIsListening(false);
        } catch (err) {
            console.error('Failed to stop recognition:', err);
        }
    }, []);

    const resetTranscript = useCallback(() => {
        setTranscript('');
    }, []);

    return {
        isListening,
        transcript,
        startListening,
        stopListening,
        resetTranscript,
        hasRecognitionSupport: hasSupport,
        error,
    };
};
