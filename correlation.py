import numpy as np
from TEMPy.MapParser import *
from TEMPy.ScoringFunctions import *
from scipy.signal import correlate
import os
from messages import Messages

""""Correlates between the target and the generated templates. Returns score matrix and direction matrix"""


def main(target_map):
    debug = True

    print Messages.START_CORRELATION
    dir_path = os.path.dirname(os.path.realpath(__file__))

    if debug and os.path.isfile(dir_path + "/correlation" + "/max_score"):
        return np.load(dir_path + "/correlation" + "/max_score"), np.load(dir_path + "/correlation" + "/max_dirs")
    max_scores = np.zeros(target_map.box_size())
    max_dirs = np.zeros(target_map.box_size(), dtype=(float, 2))
    dir_path = os.path.dirname(os.path.realpath(__file__))
    templates_dir = dir_path + "/Templates"
    sanity = 0
    for i in range(12):  # for every x rotation
        rad_in_x = (math.pi / 12) * i  # y axis rotation (in rads)
        for j in range(12):  # for every y rotation
            rad_in_y = (math.pi / 12) * j  # y axis rotation (in rads)
            template_name = "/template{0}_{1}.mrc".format(i, j)
            try:
                template_cylinder = MapParser.readMRC(templates_dir + template_name)
            except:
                print Messages.ERROR_READING_TEMPLATE_FILE.format(template_name)
            try:
                correlation_matrix = correlate(target_map.fullMap, template_cylinder.fullMap, mode="same")
            except:
                print Messages.CORRELATION_ERROR.format(template_name)

            for (x, y, z), value in np.ndenumerate(correlation_matrix):
                if value > max_scores[x, y, z]:
                    max_scores[x, y, z] = value
                    max_dirs[x, y, z] = (rad_in_x, rad_in_y)

    print Messages.DONE_CORRELATION
    if debug:

        dir_path = os.path.dirname(os.path.realpath(__file__))
        if not os.path.exists(dir_path + "/correlation"):
            os.makedirs(dir_path + "/correlation")

        score_file = open(dir_path + "/correlation" + "/max_score", "w+")
        dirs_file = open(dir_path + "/correlation" + "/max_dirs", "w+")
        np.save(score_file, max_scores)
        np.save(dirs_file, max_dirs)
        score_file.close()
        dirs_file.close()

    return max_scores, max_dirs