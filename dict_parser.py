import re
import os


def parse_txt_to_dict(file_path):
    """
    读取lib文件夹中的txt词库文件，将其转换为word_dict格式的字典
    
    Args:
        file_path (str): txt文件的路径
        
    Returns:
        dict: 形如 {单词: 释义} 的字典
    """
    word_dict = {}
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"词库文件不存在: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                # 去除行首行尾空白字符
                line = line.strip()
                
                # 跳过空行
                if not line:
                    continue
                
                # 跳过标题行和说明行
                if any(keyword in line for keyword in ['大学英语', '共', '词)', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']):
                    # 检查是否是单独的字母行（字母分类标识）
                    if len(line) == 1 and line.isalpha():
                        continue
                    # 检查是否是标题或说明行
                    if '大学英语' in line or '共' in line or '词)' in line:
                        continue
                
                # 查找第一个空格的位置
                first_space_index = line.find(' ')
                
                if first_space_index == -1:
                    # 没有空格，可能是单独的字母分类行，跳过
                    continue
                
                # 提取单词（第一个空格前的内容）
                word = line[:first_space_index].strip()
                
                # 提取释义部分（第一个空格后的内容）
                definition_part = line[first_space_index + 1:].strip()
                
                # 验证单词是否有效（只包含字母）
                if not word or not word.replace('-', '').replace("'", '').isalpha():
                    continue
                
                # 处理释义部分，提取中文释义
                # 格式通常是：[音标] 词性.中文释义
                chinese_definition = extract_definition(definition_part)
                
                if chinese_definition and word:
                    # 将单词转换为小写存储
                    word_dict[word.lower()] = chinese_definition
                    
    except Exception as e:
        print(f"读取文件时出错: {e}")

    return word_dict


def extract_definition(definition_part):
    """
    从释义部分提取词性和中文释义
    
    Args:
        definition_part (str): 包含音标、词性和中文释义的字符串
        
    Returns:
        str: 提取的词性和中文释义
    """
    # 移除音标部分 [...]
    definition_part = re.sub(r'\[.*?]', '', definition_part).strip()
    return definition_part
    
    # 下面进一步去除词性标记
    # # 查找词性标记后的中文释义
    # # 词性通常是：n. v. a. ad. prep. art. aux.v. 等
    # # 使用正则表达式匹配词性标记
    # pattern = r'^[a-zA-Z]+\.(.+)$'
    # match = re.match(pattern, definition_part)
    #
    # if match:
    #     chinese_def = match.group(1).strip()
    #     return chinese_def
    # else:
    #     # 如果没有匹配到标准格式，返回整个定义部分
    #     # 但先尝试移除可能的词性标记
    #     cleaned = re.sub(r'^[a-zA-Z]+\.', '', definition_part).strip()
    #     return cleaned if cleaned else definition_part


def load_dict_from_lib(filename):
    """
    从lib文件夹加载指定的词库文件
    
    Args:
        filename (str): 文件名，如 'CET4_edited.txt'
        
    Returns:
        dict: 解析后的词典
    """
    lib_path = os.path.join('lib', filename)
    return parse_txt_to_dict(lib_path)


def main():
    """
    主函数，演示如何使用解析器
    """
    # 解析CET4词库
    print("正在解析CET4词库...")
    cet4_dict = load_dict_from_lib('CET4_edited.txt')
    print(f"CET4词库解析完成，共 {len(cet4_dict)} 个单词")
    
    # 显示前10个单词作为示例
    print("\n前10个单词示例：")
    count = 0
    for word, definition in cet4_dict.items():
        if count >= 10:
            break
        print(f"'{word}': '{definition}'")
        count += 1
    
    print("\n" + "="*50)
    
    # 解析CET6词库
    print("正在解析CET6词库...")
    cet6_dict = load_dict_from_lib('CET6_edited.txt')
    print(f"CET6词库解析完成，共 {len(cet6_dict)} 个单词")
    
    # 显示前10个单词作为示例
    print("\n前10个单词示例：")
    count = 0
    for word, definition in cet6_dict.items():
        if count >= 10:
            break
        print(f"'{word}': '{definition}'")
        count += 1


if __name__ == '__main__':
    main()
