"use client";

import React, { useEffect, useRef } from 'react';
import { FiMic } from 'react-icons/fi';
import { useSpeechRecognition } from '@/hooks/useSpeechRecognition';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";

interface VoiceInputButtonProps {
    /** 
     * 处理识别文本的回调 
     * @param text 识别到的文本
     * @param isFinal 是否为最终结果(可选,用于优化插入逻辑)
     */
    onTranscript: (text: string, isFinal?: boolean) => void;
    className?: string;
}

export const VoiceInputButton: React.FC<VoiceInputButtonProps> = ({
    onTranscript,
    className = '',
}) => {
    const {
        isListening,
        transcript,
        startListening,
        stopListening,
        hasRecognitionSupport,
        error,
    } = useSpeechRecognition();

    // 使用 ref 记录上一次的 transcript,用于计算增量或避免重复
    const lastTranscriptRef = useRef('');

    useEffect(() => {
        if (transcript && transcript !== lastTranscriptRef.current) {
            onTranscript(transcript);
            lastTranscriptRef.current = transcript;
        }
    }, [transcript, onTranscript]);

    // 每次开始录音时重置
    useEffect(() => {
        if (isListening) {
            lastTranscriptRef.current = '';
        }
    }, [isListening]);

    // 浏览器不支持时直接不渲染,零干扰
    if (!hasRecognitionSupport) return null;

    return (
        <TooltipProvider>
            <Tooltip>
                <TooltipTrigger asChild>
                    <div
                        role="button"
                        tabIndex={0}
                        onClick={isListening ? stopListening : startListening}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                                e.preventDefault();
                                isListening ? stopListening() : startListening();
                            }
                        }}
                        className={`
              relative flex items-center justify-center w-8 h-8 rounded-full transition-all duration-200 cursor-pointer
              ${isListening
                                ? 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400'
                                : 'hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400'
                            }
              ${className}
            `}
                        aria-label={isListening ? '停止录音' : '开始语音输入'}
                    >
                        {isListening ? (
                            <>
                                <span className="absolute inset-0 rounded-full animate-ping bg-red-400 opacity-20"></span>
                                <FiMic size={18} className="animate-pulse" />
                            </>
                        ) : (
                            <FiMic size={18} />
                        )}
                    </div>
                </TooltipTrigger>
                <TooltipContent side="top">
                    <p>{error ? `错误: ${error}` : (isListening ? '点击停止' : '语音输入')}</p>
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    );
};
