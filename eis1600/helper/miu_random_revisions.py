import os
import re
import sys
import random
import subprocess


readme = """
===================================================================================
add detailed readme here to be printed out if YML file does not exist in the folder
...................................................................................
===================================================================================
"""

ymlTemplate = """

system: ... # options: mac, lin, win;
reviewer: eis1600researcher # change this to your name;
path_to_kate: kate # add absolute path to Kate on your machine; or a working alias (kate should already work)
files_to_open: 10 # the script will open 10 files by default; you can increase/decrease this value;
miu_main_path: ./data/ # the script should be run from inside the repository with MIU files
miu_specific_uri: ... # you can paste a URI of a specific book in order to focus on it

"""


def readCustomYML(text):
    text = text.strip()
    text = text.split("\n")

    dic = {}

    for t in text:
        t = t.split(":", maxsplit=1)
        key = t[0]
        val = re.sub("#.*$", "", t[1]).strip()

        dic[key] = val

    return dic


def generateDicOfMIUs(path):
    dic = {}
    for subdir, dirs, files in os.walk(path):
        for file in files:
            # process publication tf data
            if file.endswith(".EIS1600"):
                key = file
                value = os.path.join(subdir, file)
                dic[key] = value
    return(dic)


def sampleMIUs(dictionary, filterParameter, filesToOpen):
    selection = []

    for k in dictionary.keys():
        if filterParameter in k:
            selection.append(k)

    finalSelection = random.sample(selection, filesToOpen*3)

    return(finalSelection)


def main():
    if os.path.exists("file_picker.yml"):
        with open("file_picker.yml", "r", encoding="utf8") as f1:
            ymlText = f1.read().strip()
            ymlDic = readCustomYML(ymlText)

            print("===================================================================================")
            for k, v in ymlDic.items():
                print(k, ": ", v)
            print("===================================================================================")
    else:
        with open("file_picker.yml", "w", encoding="utf8") as f1:
            f1.write(ymlTemplate)

        print("===================================================================================")
        print("YML FILE HAS BEEN GENERATED; PLEASE UPDATE THE YML FILE AS DESCRIBED ==============")
        print("===================================================================================")
        print(ymlTemplate)
        print("===================================================================================")
        print("YML FILE MUST BE COMPLETED FOR THE FILE PICKER TO WORK PROPERLY. COMPLETE AND RERUN")
        print("===================================================================================")

        # print(readme)

        sys.exit()

    ################################################################################################
    # FINALIZING FILTERING PARAMETERS ##############################################################
    ################################################################################################

    if re.search(r"^\W+$", ymlDic["miu_specific_uri"]):
        filterParameter = "."
    else:
        filterParameter = ymlDic["miu_specific_uri"]

    filesToOpen = int(ymlDic["files_to_open"])
    pathToKate = ymlDic["path_to_kate"]
    path = ymlDic["miu_main_path"]
    reviewer = ymlDic["reviewer"]
    osVar = ymlDic["system"]

    ################################################################################################
    # LOADING MIU DATA, RANDOMLY SELECTING, OPENING FILES WITH KATE ################################
    ################################################################################################

    dictionary = generateDicOfMIUs(path)
    finalSample = sampleMIUs(dictionary, filterParameter, filesToOpen)

    ################################################################################################
    # OPEN MIUS from THE SELECTED SAMPLE ###########################################################
    ################################################################################################

    counter = filesToOpen

    for f in finalSample:
        with open(dictionary[f], "r", encoding="utf8") as ftIn:
            MIUcontent = ftIn.read()

            if re.search(r"reviewed\s+:\s+(False|NOT REVIEWED)", MIUcontent):
                # insert the name of the reviewer
                if re.search(r"reviewer\s+:", MIUcontent):
                    MIUcontent = re.sub(r"(reviewed\s+:)[^\n]+\n", r"\1 NOT REVIEWED\n", MIUcontent)
                    MIUcontent = re.sub(r"(reviewer\s+:)[^\n]+\n", r"\1 %s\n" % reviewer, MIUcontent)
                else:
                    MIUcontent = re.sub(
                        r"(reviewed)(\s+:)[^\n]+\n", r"\1\2 NOT REVIEWED\nreviewer\2 %s\n" % reviewer, MIUcontent
                        )

                # inserting the name of the reviewer; the reviewer will have to only change the status tag
                # upon saving and closing
                with open(dictionary[f], "w", encoding="utf8") as ftOut:
                    ftOut.write(MIUcontent)

                # NOW OPENING IN KATE FOR REVIEW
                if osVar == "mac":
                    # open on mac
                    # lineToRun = "open -a %s %s" % (pathToKate, dictionary[f])
                    # os.system(lineToRun)
                    subprocess.run(['open', '-a', pathToKate, dictionary[f]])
                elif osVar == "lin" or osVar == 'win':
                    subprocess.run([pathToKate, dictionary[f]])
                else:
                    print("Operating system is incorrect. Use: mac, lin, or win")
                    sys.exit()

                print(','.join([f, reviewer, 'in progress']))

                counter -= 1
                if counter == 0:
                    break

    print("======================================================================================")
    print("REVIEW MIU FILES IN KATE; WHEN DONE, CHANGE STATUS TO `REVIEWED`, SAVE, AND CLOSE ====")
    print("======================================================================================")
