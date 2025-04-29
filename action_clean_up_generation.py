import os
import glob

def main(**kwargs):
    directories_to_delete = []
    #directories_to_delete.append("temporary")
    directories_to_delete.append("scad_output")
    directories_to_delete.append("parts")
    directories_to_delete.append("data")
    directories_to_delete.append("navigation_oobb")
    directories_to_delete.append("navigation_oomp")
    directories_to_delete.append("oolc_production")
    directories_to_delete.append("source_files")

    files_to_save = []
    files_to_save.append("image.jpg")
    #files_to_save.append("working.yaml")
    max_range = 20
    
    for i in range(1,max_range):
        files_to_save.append(f"image_{i}.jpg")
        files_to_save.append(f"oolc_{i}.cdr")

    files_to_delete = []

    for directory in directories_to_delete:
        if os.path.exists(directory):
            #get a glob of all files in the directory recursive
            files = glob.glob(f"{directory}/**", recursive=True)
            for file in files:
                add_to_delete_list = True
                for file_to_save in files_to_save:
                    if file_to_save in file:
                        add_to_delete_list = False
                        break
                if add_to_delete_list:
                    files_to_delete.append(file)


    #check if you want to delete files
    if True:
        print("files to delete:")
        for file in files_to_delete:
            print(file)
        result = input(f"Do you want to delete {len(files_to_delete)} files? (y/n)")
        if result == "y":
            for file in files_to_delete:
                #if a file exists delete it skip directories
                if os.path.isfile(file):
                    os.remove(file)
                    print(f"deleted {file}")
            #go through and remove all empty directories recursively
            #run 20 times
            for i in range(20):
                for directory in directories_to_delete:
                    if os.path.exists(directory):
                        for root, dirs, files in os.walk(directory):
                            if len(dirs) == 0 and len(files) == 0:
                                try:
                                    os.rmdir(root)
                                    print(f"deleted {root}")
                                except:
                                    print(f".........................   failed to delete {root}")
                                    pass
        else:
            print("not deleting files")

if __name__ == "__main__":
    kwargs = {}
    main(**kwargs)