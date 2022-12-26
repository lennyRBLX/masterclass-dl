import sys, os
from masterclass import Masterclass, splash

# or by class ID:
# dl.download_course_by_class_id("gordon-ramsay-teaches-cooking")

def main():
    dl = Masterclass("_mc_session=PASTEHERE")
    class_url = sys.argv[1]
    dl.download_class_by_url(class_url)


if __name__ == "__main__":
    splash()
    main()
