import re
import os
import glob
 
  
def create_table(directory):
    # Create the table header and cells
    table_header = ''
    table_cell = ''
    
    bps_rst = [] 
    bps_titles = []
    bps_status = []
    
    max_len_title = -1
    max_len_status = -1
    max_len_bps = -1
    
    for fp in glob.glob(f'{directory}/EP*.rst'):
        split_dir = ''.join(fp.split('./blueprints/'))
        bp_rst = ''.join(split_dir.split('.rst'))
        bps_rst.append(f" :doc:`{bp_rst}<{bp_rst}/>` ")
        if max_len_bps < len(bps_rst[-1]): max_len_bps = len(bps_rst[-1])
        
        with open(fp) as origin_file:
            title = ''
            status = ''
            for line in origin_file:
                if re.findall(r':Title:', line):
                    title = ''.join(line.split(':Title:'))
                    bps_titles.append(''.join(title.split("\n")))
                    if max_len_title < len(title): max_len_title = len(title)
                    
                if re.findall(r':Status:', line):
                    status = ''.join(line.split(':Status:'))
                    bps_status.append(''.join(status.split("\n")))
                    if max_len_status < len(status): max_len_status = len(status)
                    break
    
    th_title_len = (max_len_title - len(' Title'))
    th_status_len = (max_len_status - len(' Status'))
    th_bps_len = (max_len_bps - len(' Blueprint'))
    
    table_header += f"+{'-' * max_len_bps}+{'-' * max_len_title}+{'-' * max_len_status}+\n"
    table_header += f"|{' Blueprint'}{' ' * th_bps_len}|{' Title'}{' ' * th_title_len}|{' Status'}{' ' * th_status_len}|\n"
    table_header += f"+{'=' * max_len_bps}+{'=' * max_len_title}+{'=' * max_len_status}+\n"
           
    for i in range(len(bps_rst)):
        title_space = max_len_title - len(bps_titles[i])
        status_space = max_len_status - len(bps_status[i])
        bps_space = max_len_bps - len(bps_rst[i])
        
        table_cell += f"|{bps_rst[i]}{' ' * bps_space}|{bps_titles[i]}{' ' * title_space}|{bps_status[i]}{' ' * status_space}|\n"
        table_cell += f"+{'-' * max_len_bps}+{'-' * max_len_title}+{'-' * max_len_status}+\n"
        
    return table_header + table_cell


def write_new_index_rst(directory):
    blueprints_table = create_table(directory)
    
    with open(f'{directory}/bp_table.rst', 'w') as fp:
        fp.write(blueprints_table)

if __name__ == '__main__':
    write_new_index_rst('./blueprints')    
