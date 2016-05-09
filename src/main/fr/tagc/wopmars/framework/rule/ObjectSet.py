"""
This module contains the ObjectSet class
"""
from src.main.fr.tagc.wopmars.framework.rule.IOFilePut import IOFilePut
from src.main.fr.tagc.wopmars.framework.rule.Option import Option
from src.main.fr.tagc.wopmars.utils.SetUtils import SetUtils


class ObjectSet(set):
    """
    The ObjectSet class extends the set class to redefine the __eq__
    method to fit needs of IOPut and Option objects.
    """

    def __init__(self, seq=(), s_type="", dicto={}):
        super().__init__(seq)
        # il faut pas faire ca
        assert(s_type == "input" or s_type == "output" or s_type == "params" or s_type == "wrapper" or s_type == "")
        # 2 possible types at the moment. Should i do a factory?
        # TODO ask Lionel
        if s_type == "input" or s_type == "output":
            for k in dicto:
                self.add(IOFilePut(k, dicto[k]))
        elif s_type == "params":
            for k in dicto:
                self.add(Option(k, dicto[k]))
        elif s_type == "wrapper":
            pass



    def __eq__(self, other):
        """
        For each elm of each ObjectSet, check if it equals to an other from the other set

        :param other: ObjectSet
        :return: boolean: True if it always find something that equals, False if not
        """
        # Compare the elements of self to the other's ones then from the other to the self's one
        if isinstance(self, other.__class__):
            return ((SetUtils.all_elm_of_one_set_in_one_other(self, other) and
                    SetUtils.all_elm_of_one_set_in_one_other(other, self)))
        return False

if __name__ == '__main__':
    new = ObjectSet(seq=range(5), salut=2)