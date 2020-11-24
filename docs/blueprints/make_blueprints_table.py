"""Generate Blueprints table."""
import glob
import re


def create_table(directory):
    """Create the table header and cells."""
    t_header = ''
    t_cell = ''

    bps_rst = []
    bps_titles = []
    bps_status = []

    max_len_title = -1
    max_len_status = -1
    max_len_bps = -1

    for fp_file in sorted(glob.glob(f'{directory}/EP*.rst')):
        split_dir = ''.join(fp_file.split('./blueprints/'))
        bp_rst = ''.join(split_dir.split('.rst'))
        bps_rst.append(f" :doc:`{bp_rst}<{bp_rst}/>` ")
        if max_len_bps < len(bps_rst[-1]):
            max_len_bps = len(bps_rst[-1])

        with open(fp_file) as origin_file:
            title = ''
            status = ''
            for line in origin_file:
                if re.findall(r':Title:', line):
                    title = ''.join(line.split(':Title:'))
                    bps_titles.append(''.join(title.split("\n")))
                    if max_len_title < len(title):
                        max_len_title = len(title)

                if re.findall(r':Status:', line):
                    status = ''.join(line.split(':Status:'))
                    bps_status.append(''.join(status.split("\n")))
                    if max_len_status < len(status):
                        max_len_status = len(status)
                    break

    th_title_len = max_len_title - len(' Title')
    th_status_len = max_len_status - len(' Status')
    th_bps_len = max_len_bps - len(' Blueprint')

    t_header += f"+{'-' * max_len_bps}+"
    t_header += f"{'-' * max_len_title}+{'-' * max_len_status}+\n"
    t_header += f"|{' Blueprint'}{' ' * th_bps_len}|{' Title'}"
    t_header += f"{' ' * th_title_len}|{' Status'}{' ' * th_status_len}|\n"
    t_header += f"+{'=' * max_len_bps}+{'=' * max_len_title}+"
    t_header += f"{'=' * max_len_status}+\n"

    for i, _ in enumerate(bps_rst, start=0):
        title_space = max_len_title - len(bps_titles[i])
        status_space = max_len_status - len(bps_status[i])
        bp_space = max_len_bps - len(bps_rst[i])

        name = bps_rst[i]
        title = bps_titles[i]
        status = bps_status[i]

        t_cell += f"|{name}{' ' * bp_space}|{title}{' ' * title_space}|"
        t_cell += f"{status}{' ' * status_space}|\n"
        t_cell += f"+{'-' * max_len_bps}+{'-' * max_len_title}+"
        t_cell += f"{'-' * max_len_status}+\n"

    return t_header + t_cell


def write_new_index_rst(directory):
    """Write table of blueprints in index.rst."""
    blueprints_table = create_table(directory)

    with open(f'{directory}/bp_table.rst', 'w') as fp_file:
        fp_file.write(blueprints_table)


if __name__ == '__main__':
    write_new_index_rst('./blueprints')
