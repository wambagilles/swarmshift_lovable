
import { useState, useEffect } from 'react';

type TranslationKey = string;
type Language = 'en' | 'fr';

interface Translations {
  [key: string]: any;
}

const translations: Record<Language, Translations> = {
  en: {},
  fr: {}
};

// Global state management
let globalLanguage: Language = 'en';
let globalListeners: Set<() => void> = new Set();
let isLoaded = false;

const loadTranslations = async () => {
  if (isLoaded) return;
  
  try {
    const [enModule, frModule] = await Promise.all([
      import('../locales/en.json'),
      import('../locales/fr.json')
    ]);
    
    translations.en = enModule.default;
    translations.fr = frModule.default;
    isLoaded = true;
    
    // Initialize from localStorage
    const savedLanguage = localStorage.getItem('language') as Language;
    if (savedLanguage && (savedLanguage === 'en' || savedLanguage === 'fr')) {
      globalLanguage = savedLanguage;
    }
    
    // Notify all listeners
    globalListeners.forEach(listener => listener());
  } catch (error) {
    console.error('Failed to load translations:', error);
  }
};

const notifyLanguageChange = () => {
  globalListeners.forEach(listener => listener());
};

export const useTranslation = () => {
  const [language, setLanguage] = useState<Language>(globalLanguage);
  const [isReady, setIsReady] = useState(isLoaded);

  useEffect(() => {
    if (!isLoaded) {
      loadTranslations().then(() => {
        setIsReady(true);
        setLanguage(globalLanguage);
      });
    }

    // Register listener for language changes
    const listener = () => {
      setLanguage(globalLanguage);
    };
    
    globalListeners.add(listener);
    
    return () => {
      globalListeners.delete(listener);
    };
  }, []);

  const changeLanguage = (newLanguage: Language) => {
    globalLanguage = newLanguage;
    localStorage.setItem('language', newLanguage);
    notifyLanguageChange();
  };

  const t = (key: TranslationKey, params?: Record<string, string | number>): string => {
    if (!isReady) return key;
    
    const keys = key.split('.');
    let value: any = translations[language];
    
    for (const k of keys) {
      if (value && typeof value === 'object') {
        value = value[k];
      } else {
        return key; // Return the key if translation not found
      }
    }
    
    if (typeof value !== 'string') {
      return key;
    }
    
    // Replace parameters in the translation
    if (params) {
      return value.replace(/\{(\w+)\}/g, (match, param) => {
        return params[param]?.toString() || match;
      });
    }
    
    return value;
  };

  return {
    t,
    language,
    changeLanguage,
    isReady
  };
};
