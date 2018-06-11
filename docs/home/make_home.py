import os
import glob

def delete_old_rst(directory):
    for fp in glob.glob(f'{directory}/*.rst'):
        os.remove(fp)

def create_toc_tree(directory, files):
    toc_tree_text = ['.. toctree::\n', '  :maxdepth: 3\n', '  :hidden:\n','\n']
    for file_name in files:
        if file_name == 'index':
            continue
        toc_tree_text.append(f'  {directory}/{file_name}\n')

    return toc_tree_text


def write_new_rst(directory, readme_path):
    readme = []
    files = ['index']
    sections = [0]
    # READ THE README
    with open(readme_path) as fp:
        readme = fp.readlines()

    # CAlCULATE THE SECTIONS
    count = 0
    tags = 0
    for line in readme:
        if '****\n' in line:
            sections.append(count-2)
            file_name = readme[count-1].strip()
            file_name = file_name.lower().replace(' ', '_')
            files.append(file_name)
        count += 1
        if '.. TAGs\n' in line:
            tags = count
            break

    toc_tree_text = create_toc_tree(directory, files)

    # FOR EACH SECTION CREATE A NEW FILE INTO THE INDEX FOLDER
    for index, section in enumerate(sections):
        path = f'{directory}/{files[index]}.rst'

        with open(path,'w') as fp:
            if index == len(sections)-1:
                start = section
                end = tags - 1
            else:
                start = section
                end = sections[index+1]

            fp.write(''.join(readme[start:end]))

            if index == 0:
                fp.write('\n')
                fp.write(''.join(readme[tags-1:]))

    with open('index.rst', 'w') as fp:
        fp.write(f'.. include:: {directory}/index.rst\n\n')
        fp.write(''.join(toc_tree_text))

if __name__ == '__main__':
    delete_old_rst('./home')
    write_new_rst('./home', '../README.rst')
