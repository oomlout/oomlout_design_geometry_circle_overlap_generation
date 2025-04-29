import os
import yaml
import time

def main(**kwargs):

    #import details from yaml file
    file_configuration_yaml = 'configuration\\working.yaml'
    with open(file_configuration_yaml, 'r') as stream:
        try:
            details = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            #don't handle just raise the exception
            raise exc            
            #print(exc)
    kwargs.update(details)

    #create oomp_id
    kwargs = create_oomp_id(**kwargs)

    create_oomp_folder(**kwargs)

    #clone repo
    clone_rep(**kwargs)

    #copy files across
    copy_files(**kwargs)



def clone_rep(**kwargs):
    print('Cloning repo')
    #clone repo
    repo = kwargs.get('oomp_open_hardware_project_repo',"")
    if repo == "":
        print('Repo not specified')
        return
    
    #create temporary directory
    temp_dir = 'temporary'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    #clone repo into temporary directory
    os.system('git clone ' + repo + ' ' + temp_dir)

    #create a source directory
    source_dir = 'source'
    if not os.path.exists(source_dir):
        os.makedirs(source_dir)

    #copy files from temporary directory to source directory using os.system call
    os.system('xcopy /E /Y ' + temp_dir + ' ' + source_dir)

    #remove the git directory in the source folder using os.system
    os.system('rmdir /S /Q ' + source_dir + '\\.git')
    

    print('        Done')

def copy_files(**kwargs):
    file_list = kwargs.get('oomp_open_hardware_project_file_list',[])
    oomp_id = kwargs.get('oomp_id',"")
    folder_oomp = f"parts\\{oomp_id}"
    #file copying
    print('Copying files')
    for file_details in file_list:
        source_file_base = file_details.get('source_file',"")
        if source_file_base != "":
            destination_file_base = file_details.get('destination_file',"")
            
            source_file_full = f"source\\{source_file_base}"
            destination_file_full = f"{folder_oomp}\\{destination_file_base}"
            if os.path.exists(source_file_full):
                #replace / with \\
                destination_file_full = destination_file_full.replace('/','\\')
                source_file_full = source_file_full.replace('/','\\')
                #use xcopy
                os.system(f'copy /Y "{source_file_full}" "{destination_file_full}"')                
                print('    Copied: ' + source_file_full + ' to ' + destination_file_full)
            else:
                print('    File does not exist: ' + source_file_full)
                e = Exception('File does not exist: ' + source_file_full)
                raise e
    print('        Done')


def create_oomp_folder(**kwargs):
    print('Creating oomp folder')
    oomp_id = kwargs.get('oomp_id',"")

    folder = f"parts\\{oomp_id}"
    if not os.path.exists(folder):
        os.makedirs(folder)
        print('    Created folder: ' + folder)
    else:
        print('    Folder already exists: ' + folder)

    file_working_yaml = folder + '\\working.yaml'

    print ('    Writing working.yaml')
    with open(file_working_yaml, 'w') as stream:
        try:
            yaml.dump(kwargs, stream)
        except yaml.YAMLError as exc:
            #don't handle just raise the exception
            raise exc            
            #print(exc)
        
    print('        Done')

def create_oomp_id(**kwargs):
    print('Creating oomp_id')
    id_elements = []
    id_elements.append("oomp_classification")
    id_elements.append("oomp_type")
    id_elements.append("oomp_size")
    id_elements.append("oomp_color")
    id_elements.append("oomp_description_main")
    id_elements.append("oomp_description_extra")
    id_elements.append("oomp_manufacturer")
    id_elements.append("oomp_part_number")

    oomp_id = ''
    for element in id_elements:
        ele = kwargs.get(element,"")
        if ele != "":
            oomp_id += ele + '_'
        element_name_raw = element.replace('oomp_','')
        kwargs.update({element_name_raw:ele})    
    oomp_id = oomp_id[:-1]

    md5 = md5_from_string(oomp_id)
    kwargs['md5'] = md5
    kwargs['md5_6'] = md5[:6]
    kwargs['md5_6_alpha'] = hex_to_alpha(md5[:6])
    kwargs['md5_10'] = md5[:10]
    kwargs['md5_10_alpha'] = hex_to_alpha(md5[:10])


    kwargs['oomp_id'] = oomp_id
    folder = f"parts\\{oomp_id}"
    kwargs['folder'] = folder
    print('    oomp_id: ' + oomp_id)
    print("        Done")
    return kwargs

def md5_from_string(string):
    import hashlib
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()

def hex_to_alpha(hex_str):
    # Convert hex string to integer
    num = int(hex_str, 16)
    
    # Define the mapping of integers to alphanumeric characters
    alpha_map = 'abcdefghijklmnopqrstuvwxyz0123456789'
    
    # Get the corresponding alphanumeric character
    if num < len(alpha_map):
        return alpha_map[num]
    else:
        return None  # Return None if the number is out of range

    

if __name__ == '__main__':
    kwargs = {}
    main(**kwargs)