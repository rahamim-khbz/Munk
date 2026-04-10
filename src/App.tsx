/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, useRef } from 'react';
import { GoogleGenAI, Type } from '@google/genai';
import { motion, AnimatePresence } from 'motion/react';
import { 
  BookOpen, 
  Languages, 
  Type as TypeIcon, 
  Moon, 
  Sun, 
  Coffee, 
  Edit3, 
  Check, 
  AlertCircle,
  Loader2,
  SplitSquareHorizontal,
  AlignLeft,
  Square,
  Image as ImageIcon,
  Upload
} from 'lucide-react';

type Theme = 'light' | 'dark' | 'sepia';
type Engine = 'gemini-3-flash-preview' | 'gemma-2-2b-it' | 'gemma-2-9b-it' | 'native';
type ViewMode = 'single' | 'split';

const DEFAULT_TEXT = ``;

export default function App() {
  const [originalText, setOriginalText] = useState(DEFAULT_TEXT);
  const [isEditing, setIsEditing] = useState(true);
  const [editText, setEditText] = useState(DEFAULT_TEXT);
  const [isExtension, setIsExtension] = useState(false);
  
  const [theme, setTheme] = useState<Theme>('light');
  const [fontSize, setFontSize] = useState(18);
  const [engine, setEngine] = useState<Engine>('gemini-3-flash-preview');
  const [viewMode, setViewMode] = useState<ViewMode>('split');
  
  const [translatedParagraphs, setTranslatedParagraphs] = useState<string[]>([]);
  const [isTranslating, setIsTranslating] = useState(false);
  const [isExtractingText, setIsExtractingText] = useState(false);
  const [extractStatus, setExtractStatus] = useState<string>('');
  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const [rawOcrText, setRawOcrText] = useState<string>('');
  const [autoTranslatePending, setAutoTranslatePending] = useState(false);
  const [ocrEngine, setOcrEngine] = useState<'gemini-3.1-pro-preview' | 'gemini-3-flash-preview'>('gemini-3.1-pro-preview');
  const [error, setError] = useState<string | null>(null);
  const cancelRef = useRef(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Check if running as a Chrome Extension and extract text
  useEffect(() => {
    if (typeof chrome !== 'undefined' && chrome.tabs && chrome.scripting) {
      setIsExtension(true);
      
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const activeTab = tabs[0];
        if (activeTab && activeTab.id) {
          chrome.scripting.executeScript({
            target: { tabId: activeTab.id },
            func: () => {
              // This function runs in the context of the active web page
              const article = document.querySelector('article');
              if (article) return article.innerText;
              
              // Fallback: gather all paragraphs that have substantial text
              const paragraphs = Array.from(document.querySelectorAll('p'))
                .map(p => p.innerText.trim())
                .filter(text => text.length > 40);
                
              if (paragraphs.length > 0) {
                return paragraphs.join('\n\n');
              }
              
              return document.body.innerText;
            }
          }, (results) => {
            if (results && results[0] && results[0].result) {
              const extractedText = results[0].result;
              setOriginalText(extractedText);
              setEditText(extractedText);
            }
          });
        }
      });
    }
  }, []);

  const originalParagraphs = originalText.split('\n').filter(p => p.trim().length > 0);

  const parts = originalText.split(/([.!?\n]+)/);
  const sentences: string[] = [];
  for (let i = 0; i < parts.length; i += 2) {
    const text = parts[i];
    const delim = parts[i + 1] || '';
    const sentence = (text + delim).trim();
    if (sentence) sentences.push(sentence);
  }

  const originalBlocks: string[] = [];
  for (let i = 0; i < sentences.length; i += 1) {
    originalBlocks.push(sentences.slice(i, i + 1).join(' '));
  }

  const processImage = async (file: File) => {
    if (!file.type.startsWith('image/')) return;
    
    setIsExtractingText(true);
    setExtractStatus('Extracting text from image...');
    setRawOcrText('');
    setError(null);
    
    try {
      const dataUrl = await new Promise<string>((resolve) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result as string);
        reader.readAsDataURL(file);
      });
      
      setPreviewImage(dataUrl);
      const base64Data = dataUrl.split(',')[1];

      const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
      
      // Step 1: Raw extraction
      const extractResponse = await ai.models.generateContent({
        model: ocrEngine,
        contents: [
          "This image contains Hebrew/Aramaic text. It may be written in standard square letters or Rashi script. Your task is to transcribe it accurately into standard Hebrew square letters.\n\nCRITICAL INSTRUCTIONS:\n1. Read strictly from RIGHT to LEFT, line by line.\n2. Preserve the exact word order as it appears in the image. Do not reverse the words.\n3. Do not attempt to correct grammar or guess missing words. Transcribe exactly what is visible.\n4. Pay close attention to similar-looking letters in Rashi script.\n\nReturn ONLY the transcribed text without any markdown formatting.",
          { inlineData: { mimeType: file.type, data: base64Data } }
        ]
      });
      
      const rawText = extractResponse.text;
      
      if (rawText) {
        setRawOcrText(rawText);
        // Step 2: Reformatting
        setExtractStatus('Reconstructing logical sentences...');
        const formatResponse = await ai.models.generateContent({
          model: ocrEngine,
          contents: [
            `Here is raw Hebrew/Aramaic text extracted from the image:\n\n${rawText}\n\nPlease reconstruct this text into continuous, logical paragraphs.\n\nCRITICAL INSTRUCTIONS:\n1. Remove all arbitrary visual line breaks from the raw text.\n2. Keep sentences continuous and together.\n3. Reintroduce sentence breaks and paragraph breaks ONLY where the logical punctuation dictates.\n4. Preserve the exact right-to-left word order and spelling.\n\nReturn ONLY the continuous reformatted text, without any markdown formatting or additional comments.`,
            { inlineData: { mimeType: file.type, data: base64Data } }
          ]
        });
        
        if (formatResponse.text) {
          const newText = editText.trim() === '' ? formatResponse.text : editText + '\n\n' + formatResponse.text;
          setEditText(newText);
          setOriginalText(newText);
          setIsEditing(false);
          setAutoTranslatePending(true);
        }
      }
    } catch (err: any) {
      console.error("OCR Error:", err);
      setError(err.message || "Failed to extract text from image.");
    } finally {
      setIsExtractingText(false);
      setExtractStatus('');
      setPreviewImage(null);
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    if (!isEditing) return;
    const items = e.clipboardData?.items;
    if (!items) return;
    
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        e.preventDefault();
        const file = items[i].getAsFile();
        if (file) processImage(file);
        break;
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) processImage(file);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleStop = () => {
    cancelRef.current = true;
    setIsTranslating(false);
  };

  const handleTranslate = async () => {
    if (originalBlocks.length === 0) return;
    
    cancelRef.current = false;
    setIsTranslating(true);
    setError(null);
    setViewMode('split');
    
    try {
      if (engine === 'native') {
        // Mocking native translation API since it's experimental and not widely available
        // In a real Chrome extension, we'd use chrome.tabs.executeScript or the new window.translation API
        if ('translation' in window && typeof (window as any).translation.createTranslator === 'function') {
           // Attempt to use Chrome's experimental translation API
           const translator = await (window as any).translation.createTranslator({ sourceLanguage: 'he', targetLanguage: 'en' });
           const results = await Promise.all(originalBlocks.map(p => translator.translate(p)));
           setTranslatedParagraphs(results);
        } else {
          throw new Error("Chrome's native Translator API is not available in this environment. Falling back to Gemini.");
        }
      } else {
        // Use Gemini for high-quality contextual translation
        const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
        
        const CHUNK_SIZE = 4; // Smaller chunks for faster parallel processing
        const chunks = [];
        for (let i = 0; i < originalBlocks.length; i += CHUNK_SIZE) {
          chunks.push(originalBlocks.slice(i, i + CHUNK_SIZE));
        }

        // Initialize empty array to show translations as they arrive
        setTranslatedParagraphs(new Array(originalBlocks.length).fill(''));

        const BATCH_SIZE = 3; // Process 3 chunks (12 sentences) at a time to allow stopping
        const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

        for (let i = 0; i < chunks.length; i += BATCH_SIZE) {
          if (cancelRef.current) break;
          
          if (i > 0) {
            // Add a small delay between batches to help prevent rate limiting
            await sleep(1000);
          }
          
          const batch = chunks.slice(i, i + BATCH_SIZE);
          await Promise.all(batch.map(async (chunk, batchIndex) => {
            const chunkIndex = i + batchIndex;
            if (cancelRef.current) return;
            
            let retries = 0;
            const maxRetries = 4;
            
            while (retries <= maxRetries) {
              try {
                const isGemma = engine.includes('gemma');
                const config = isGemma ? undefined : {
                  responseMimeType: 'application/json',
                  responseSchema: {
                    type: Type.ARRAY,
                    items: { type: Type.STRING }
                  }
                };

                const response = await ai.models.generateContent({
                  model: engine === 'native' ? 'gemini-3-flash-preview' : engine,
                  contents: `Translate the following Hebrew or Judeo-Arabic text into English. Return ONLY a valid JSON array of strings in the exact same order and length. Maintain the tone and nuances of the original text. Do not include any markdown formatting.\n\n${JSON.stringify(chunk)}`,
                  config
                });
                
                if (cancelRef.current) return;

                if (response.text) {
                  const cleanText = response.text.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
                  const translatedChunk = JSON.parse(cleanText);
                  if (Array.isArray(translatedChunk)) {
                    setTranslatedParagraphs(prev => {
                      const updated = [...prev];
                      for (let j = 0; j < translatedChunk.length; j++) {
                        updated[chunkIndex * CHUNK_SIZE + j] = translatedChunk[j];
                      }
                      return updated;
                    });
                  }
                }
                break; // Success, exit retry loop
              } catch (chunkErr: any) {
                if (cancelRef.current) return;
                
                const errorStr = chunkErr instanceof Error ? chunkErr.message : JSON.stringify(chunkErr);
                const isRateLimit = errorStr.includes('429') || errorStr.includes('RESOURCE_EXHAUSTED') || errorStr.includes('quota');
                
                if (isRateLimit && retries < maxRetries) {
                  retries++;
                  const delay = Math.pow(2, retries) * 1000 + Math.random() * 1000; // Exponential backoff with jitter
                  console.warn(`Rate limit hit for chunk ${chunkIndex}. Retrying in ${Math.round(delay)}ms... (Attempt ${retries} of ${maxRetries})`);
                  await sleep(delay);
                  continue; // Retry
                }
                
                console.error("Chunk translation error:", chunkErr);
                setTranslatedParagraphs(prev => {
                  const updated = [...prev];
                  for (let j = 0; j < chunk.length; j++) {
                    updated[chunkIndex * CHUNK_SIZE + j] = "⚠️ Translation failed for this section.";
                  }
                  return updated;
                });
                break; // Break on non-retriable error or max retries
              }
            }
          }));
        }
      }
    } catch (err: any) {
      console.error(err);
      if (engine === 'native') {
        // Fallback to Gemini if native fails
        setEngine('gemini');
        setError("Native translation unavailable. Switched to Gemini. Please try again.");
      } else {
        setError(err.message || "An error occurred during translation.");
      }
    } finally {
      if (!cancelRef.current) {
        setIsTranslating(false);
      }
    }
  };

  useEffect(() => {
    if (autoTranslatePending && originalBlocks.length > 0) {
      setAutoTranslatePending(false);
      handleTranslate();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoTranslatePending, originalBlocks.length]);

  const handleSaveEdit = () => {
    setOriginalText(editText);
    setIsEditing(false);
    setTranslatedParagraphs([]); // Clear translation when text changes
  };

  // Apply theme to body
  useEffect(() => {
    document.body.className = `theme-${theme} transition-colors duration-300 min-h-screen`;
  }, [theme]);

  return (
    <div className={`min-h-screen flex flex-col theme-${theme}`}>
      {!isExtension && (
        <div className="bg-blue-50 dark:bg-blue-900/30 border-b border-blue-200 dark:border-blue-800 px-4 py-2 text-sm text-blue-800 dark:text-blue-200 flex justify-center text-center">
          Running in Web Preview. To use on any website, export this project as a ZIP and load it as a Chrome Extension.
        </div>
      )}
      {/* Toolbar */}
      <header className="sticky top-0 z-10 backdrop-blur-md bg-opacity-80 border-b border-gray-200 dark:border-gray-800 shadow-sm px-4 py-3 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2 font-semibold text-lg">
          <BookOpen className="w-6 h-6 text-blue-600 dark:text-blue-400" />
          <span>The Tourgeman</span>
        </div>
        
        <div className="flex items-center gap-4 overflow-x-auto pb-1 sm:pb-0">
          {/* View Mode Toggle */}
          <div className="flex items-center bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
            <button 
              onClick={() => setViewMode('single')}
              className={`p-1.5 rounded-md transition-colors ${viewMode === 'single' ? 'bg-white dark:bg-gray-700 shadow-sm' : 'hover:bg-gray-200 dark:hover:bg-gray-700'}`}
              title="Single View"
            >
              <AlignLeft className="w-4 h-4" />
            </button>
            <button 
              onClick={() => setViewMode('split')}
              className={`p-1.5 rounded-md transition-colors ${viewMode === 'split' ? 'bg-white dark:bg-gray-700 shadow-sm' : 'hover:bg-gray-200 dark:hover:bg-gray-700'}`}
              title="Side-by-Side View"
            >
              <SplitSquareHorizontal className="w-4 h-4" />
            </button>
          </div>

          <div className="h-6 w-px bg-gray-300 dark:bg-gray-700"></div>

          {/* Theme Selector */}
          <div className="flex items-center gap-1">
            <button onClick={() => setTheme('light')} className={`p-2 rounded-full ${theme === 'light' ? 'bg-gray-200 dark:bg-gray-800' : 'hover:bg-gray-100 dark:hover:bg-gray-800'}`} title="Light Mode"><Sun className="w-4 h-4" /></button>
            <button onClick={() => setTheme('sepia')} className={`p-2 rounded-full ${theme === 'sepia' ? 'bg-[#e4dcc8] text-[#5b4636]' : 'hover:bg-[#e4dcc8] text-[#5b4636]'}`} title="Sepia Mode"><Coffee className="w-4 h-4" /></button>
            <button onClick={() => setTheme('dark')} className={`p-2 rounded-full ${theme === 'dark' ? 'bg-gray-800 text-white' : 'hover:bg-gray-200 dark:hover:bg-gray-800'}`} title="Dark Mode"><Moon className="w-4 h-4" /></button>
          </div>

          <div className="h-6 w-px bg-gray-300 dark:bg-gray-700"></div>

          {/* Font Size */}
          <div className="flex items-center gap-2">
            <TypeIcon className="w-4 h-4 opacity-70" />
            <button onClick={() => setFontSize(Math.max(12, fontSize - 2))} className="w-8 h-8 flex items-center justify-center rounded hover:bg-gray-200 dark:hover:bg-gray-800 font-medium">-</button>
            <span className="text-sm w-6 text-center">{fontSize}</span>
            <button onClick={() => setFontSize(Math.min(32, fontSize + 2))} className="w-8 h-8 flex items-center justify-center rounded hover:bg-gray-200 dark:hover:bg-gray-800 font-medium">+</button>
          </div>

          <div className="h-6 w-px bg-gray-300 dark:bg-gray-700"></div>

          {/* Translation Controls */}
          <div className="flex items-center gap-2">
            <select
              value={engine}
              onChange={(e) => setEngine(e.target.value as Engine)}
              className="bg-transparent border border-gray-300 dark:border-gray-700 rounded-md px-2 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none hidden sm:block"
            >
              <option value="gemini-3-flash-preview">Gemini 3 Flash</option>
              <option value="gemma-2-2b-it">Gemma 2 2B (Lightweight)</option>
              <option value="gemma-2-9b-it">Gemma 2 9B (Balanced)</option>
              <option value="native">Native (Exp)</option>
            </select>

            {isTranslating ? (
              <button 
                onClick={handleStop}
                className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-1.5 rounded-md text-sm font-medium transition-colors"
              >
                <Square className="w-4 h-4 fill-current" />
                Stop
              </button>
            ) : (
              <button 
                onClick={handleTranslate}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-1.5 rounded-md text-sm font-medium transition-colors"
              >
                <Languages className="w-4 h-4" />
                Translate to English
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3 text-red-800 dark:text-red-200">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <p className="text-sm">{error}</p>
          </div>
        )}

        {isEditing ? (
          <div className="max-w-3xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-300">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Edit Text</h2>
              <div className="flex items-center gap-2">
                <select
                  value={ocrEngine}
                  onChange={(e) => setOcrEngine(e.target.value as any)}
                  disabled={isExtractingText}
                  className="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-md px-2 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none hidden sm:block disabled:opacity-50"
                >
                  <option value="gemini-3.1-pro-preview">OCR: Pro (Accurate)</option>
                  <option value="gemini-3-flash-preview">OCR: Flash (Fast)</option>
                </select>
                <input 
                  type="file" 
                  accept="image/*" 
                  className="hidden" 
                  ref={fileInputRef} 
                  onChange={handleFileChange} 
                />
                <button 
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isExtractingText}
                  className="flex items-center gap-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 px-4 py-2 rounded-md transition-colors disabled:opacity-50"
                >
                  {isExtractingText ? <Loader2 className="w-4 h-4 animate-spin" /> : <ImageIcon className="w-4 h-4" />}
                  {isExtractingText ? 'Extracting...' : 'Upload Image'}
                </button>
                <button 
                  onClick={handleSaveEdit}
                  className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md transition-colors"
                >
                  <Check className="w-4 h-4" /> Save
                </button>
              </div>
            </div>
            <div className="relative">
              <textarea
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                onPaste={handlePaste}
                disabled={isExtractingText}
                className={`w-full h-[60vh] p-4 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg shadow-inner focus:ring-2 focus:ring-blue-500 outline-none resize-none ${isExtractingText ? 'opacity-50' : ''}`}
                style={{ fontSize: `${fontSize}px`, fontFamily: 'inherit' }}
                placeholder="Paste your article, text, or an image here..."
              />
              {isExtractingText && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none rounded-lg overflow-hidden">
                  {previewImage && (
                    <img 
                      src={previewImage} 
                      alt="OCR Preview" 
                      className="absolute inset-0 w-full h-full object-contain opacity-20 grayscale"
                    />
                  )}
                  
                  <AnimatePresence>
                    {extractStatus === 'Reformatting text to match image...' && rawOcrText && (
                      <motion.div
                        initial={{ top: '60%', opacity: 0, scale: 0.9 }}
                        animate={{ top: '15%', opacity: 1, scale: 1 }}
                        transition={{ duration: 1.5, ease: "easeOut" }}
                        className="absolute left-0 right-0 flex justify-center z-20"
                      >
                        <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm px-6 py-3 rounded-lg shadow-xl max-w-[90%] border border-blue-200 dark:border-blue-800">
                          <p className="font-serif text-2xl text-gray-800 dark:text-gray-200" dir="rtl">
                            {rawOcrText.split('\n').find(line => line.trim().length > 0)}
                          </p>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  <div className="bg-white/90 dark:bg-gray-900/90 px-6 py-4 rounded-lg shadow-lg flex flex-col items-center gap-3 relative z-30">
                    <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                    <p className="font-medium">{extractStatus}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="animate-in fade-in duration-500">
            <div className="flex justify-end mb-6 max-w-5xl mx-auto">
              <button 
                onClick={() => { setIsEditing(true); setEditText(originalText); }}
                className="flex items-center gap-2 text-sm opacity-70 hover:opacity-100 transition-opacity"
              >
                <Edit3 className="w-4 h-4" /> Edit Text
              </button>
            </div>

            <div className={`mx-auto ${viewMode === 'split' && translatedParagraphs.length > 0 ? 'max-w-6xl' : 'max-w-3xl'}`}>
              <AnimatePresence mode="wait">
                {translatedParagraphs.length > 0 ? (
                  <motion.div
                    key="split-view"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    {originalBlocks.map((block, index) => (
                      <motion.div 
                        key={index} 
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        transition={{ duration: 0.5, delay: index * 0.15, ease: "easeOut" }}
                        style={{ overflow: 'hidden' }}
                      >
                        <div className={`mb-8 ${viewMode === 'split' ? 'flex flex-col md:flex-row gap-6 md:gap-12' : ''}`}>
                          {/* Original Text */}
                          <div 
                            className={`font-serif leading-relaxed ${viewMode === 'split' ? 'w-full md:w-1/2' : 'w-full'}`}
                            style={{ fontSize: `${fontSize}px`, direction: 'rtl', textAlign: 'justify' }}
                          >
                            {block}
                          </div>
                          
                          {/* Translated Text */}
                          {translatedParagraphs[index] ? (
                            <div 
                              className={`font-serif leading-relaxed translated-text ${viewMode === 'split' ? 'w-full md:w-1/2 mt-4 md:mt-0 border-l-4 md:border-l-0 border-blue-200 dark:border-blue-900 pl-4 md:pl-0' : 'w-full mt-4 border-l-4 border-blue-200 dark:border-blue-900 pl-4'}`}
                              style={{ fontSize: `${fontSize}px`, direction: 'ltr', textAlign: 'left' }}
                            >
                              {translatedParagraphs[index]}
                            </div>
                          ) : (
                            isTranslating && (
                              <div className={`flex items-center justify-center ${viewMode === 'split' ? 'w-full md:w-1/2 mt-4 md:mt-0' : 'w-full mt-4'} opacity-50`}>
                                <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
                              </div>
                            )
                          )}
                        </div>
                      </motion.div>
                    ))}
                  </motion.div>
                ) : (
                  <motion.div
                    key="paragraph-view"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    {originalParagraphs.map((paragraph, index) => (
                      <div 
                        key={index} 
                        className="mb-8"
                      >
                        <div 
                          className="font-serif leading-relaxed w-full"
                          style={{ fontSize: `${fontSize}px`, direction: 'rtl', textAlign: 'justify' }}
                        >
                          {paragraph}
                        </div>
                      </div>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
