import re
import os
import glob

def create_toc_tree():
    main_title = '\n' + '#' * 10 + '\nBlueprints\n' + '#' * 10 + '\n'
    sub_title = '\nTable of Blueprints\n\n'
    
    file_header = [':orphan:\n']
    file_header.append(main_title)
    file_header.append(sub_title)
    
    toc_tree_text = ['.. toctree::\n', '  :glob:\n', '  :hidden:\n','\n', '  EP*\n\n',]
    
    file_header = ''.join(file_header)
    toc_tree_text = ''.join(toc_tree_text)
    
    return file_header, toc_tree_text
    
    
def create_table(directory):
    #Create the table header
    table_header = ''
    table_header += '+' + '-' * 23 + '+' + '-' * 82 + '+' + '-' * 20 + '+\n'
    table_header += '|' + ' Blueprint'  + ' ' * 13 + '|' + ' Title' + ' ' * 76 + '|' + ' Status' + ' ' * 13 + '|\n'
    table_header += '+' + '=' * 23 + '+' + '=' * 82 + '+' + '=' * 20 + '+\n'
    
    
    table_cell = ''
    for fp in glob.glob(f'{directory}/EP*.rst'):
        split_dir = ''.join(fp.split('./blueprints/'))
        bp_rst = ''.join(split_dir.split('.rst'))
    
        with open(fp) as origin_file:
            title = 'Metadata not define for :Title:'
            status = 'Metadata not define for :Status:'
            for line in origin_file:
                if re.findall(r':Title:', line):
                    title = ''.join(line.split(':Title:'))
                    title = ''.join(title.split("\n"))
                if re.findall(r':Status:', line):
                    status = ''.join(line.split(':Status:'))
                    status = ''.join(status.split("\n"))
                    break
                
        title_space = 82 - (len(title))
        status_space = 20 - (len(status))
        table_cell += '|' + ' :doc:`'+ bp_rst + '<' + bp_rst + '/>` '  + ' ' + '|' + title + ' ' * title_space + '|' + status + ' ' * status_space + '|\n'
        table_cell += '+' + '-' * 23 + '+' + '-' * 82 + '+' + '-' * 20 + '+\n'
        
    return table_header + table_cell


def write_new_index_rst(directory):
    file_header, toc_tree_text = create_toc_tree()
    blueprints_table = create_table(directory)
    
    with open(f'{directory}/index.rst', 'w') as fp:
        fp.write(file_header)
        fp.write(toc_tree_text)
        fp.write(blueprints_table)


if __name__ == '__main__':
    write_new_index_rst('./blueprints')    
