"""语言管理器"""

import json
import os


class LanguageManager:
    def __init__(self, config_file="config.json", lang_dir="lang"):
        self.config_file = config_file
        self.lang_dir = lang_dir
        self.config = self._load_config()
        self.languages = self._load_languages()
        self.current_language = self._get_current_language()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def _save_config(self):
        """保存配置文件"""
        try:
            # 读取现有配置
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
            
            # 更新语言设置
            config["language"] = self.current_language
            
            # 保存配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def _load_languages(self):
        """从lang目录加载所有语言文件"""
        languages = {}
        
        if not os.path.exists(self.lang_dir):
            return languages
        
        try:
            for filename in os.listdir(self.lang_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.lang_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            lang_data = json.load(f)
                            
                            # 验证语言文件格式
                            if 'metadata' in lang_data and 'translations' in lang_data:
                                metadata = lang_data['metadata']
                                lang_code = metadata.get('code', filename[:-5])
                                languages[lang_code] = {
                                    'name': metadata.get('name', lang_code),
                                    'code': lang_code,
                                    'author': metadata.get('author', 'Unknown'),
                                    'translations': lang_data['translations'],
                                    'filename': filename
                                }
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            pass
        
        return languages
    
    def _get_current_language(self):
        """获取当前语言"""
        saved_lang = self.config.get("language")
        
        # 如果保存的语言存在，使用它
        if saved_lang and saved_lang in self.languages:
            return saved_lang
        
        # 否则使用第一个可用的语言
        if self.languages:
            return list(self.languages.keys())[0]
        
        # 如果没有语言文件，使用默认语言
        return "zh_CN"
    
    def reload_languages(self):
        """重新加载语言文件（用于用户添加新语言后刷新）"""
        old_current = self.current_language
        self.languages = self._load_languages()
        
        # 如果当前语言不在新加载的语言列表中，切换到第一个可用语言
        if self.current_language not in self.languages:
            if self.languages:
                self.current_language = list(self.languages.keys())[0]
            else:
                self.current_language = "zh_CN"
        
        # 保存新语言设置
        self._save_config()
        
        return old_current != self.current_language
    
    def set_language(self, language_code):
        """设置当前语言"""
        if language_code in self.languages:
            self.current_language = language_code
            self._save_config()
            return True
        return False
    
    def get_language(self):
        """获取当前语言代码"""
        return self.current_language
    
    def get_display_name(self, language_code):
        """获取语言显示名称"""
        if language_code in self.languages:
            return self.languages[language_code]['name']
        return language_code
    
    def get_all_languages(self):
        """获取所有支持的语言列表 (language_code, display_name)"""
        return [(code, data['name']) for code, data in self.languages.items()]
    
    def get_language_info(self, language_code):
        """获取语言完整信息"""
        if language_code in self.languages:
            return self.languages[language_code]
        return None
    
    def translate(self, key, default=None):
        """获取翻译文本
        
        优先级：
        1. 当前语言中的翻译
        2. 英语(en_US)中的翻译（如果存在）
        3. 默认值
        4. 翻译键本身
        """
        if default is None:
            default = key
        
        # 首先尝试从当前语言获取翻译
        if self.current_language in self.languages:
            translations = self.languages[self.current_language]['translations']
            if key in translations:
                return translations[key]
        
        # 如果当前语言中没有找到，尝试从英语(en_US)获取翻译
        if 'en_US' in self.languages and self.current_language != 'en_US':
            translations = self.languages['en_US']['translations']
            if key in translations:
                return translations[key]
        
        # 都没有找到，返回默认值
        return default
    
    def tr(self, key, default=None):
        """translate的简写"""
        return self.translate(key, default)
    
    def get_translations(self, language_code):
        """获取指定语言的所有翻译"""
        if language_code in self.languages:
            return self.languages[language_code]['translations']
        return {}
    
    def get_available_languages(self):
        """获取所有可用语言的代码列表"""
        return list(self.languages.keys())
