# -*- coding: utf-8 -*-
"""
TODO fix the problem for 0 sphere, cyl, axis
"""
import re, os.path

SCAdict={'f':('subjectdata','FarVisionSCA'),
              'n':('subjectdata','NearVisionSCA'),
              'F':('finalprescriptiondata','FarVisionSCA)'),
              'N':('finalprescriptiondata','NearVisionSCA'),
              'O':('ARdata','ObjectiveSCA'),
               }
keysOR = ('sph_od','cyl_od','axis_od')
keysOS = ('sph_os','cyl_os','axis_os')
#print 'hello'
# Les points de coupures semblent etre toujours les memes
# les données recherchées peuvent etre récupérée par l'index
# S=morceaux[1] C=morceaux[2] A=Morceaux[3]
#constant
coupures = [28, 30, 36, 42, 45] 

def trimzero(val):
    """Trim zero value if there is one at the 2nd decimal
    needed if there is a selection fields with no zero at the 2nd decimal
    in Odoo
    
    val : string from the rt5100
    
    example: '+ 2.20' return '+ 2.2'
    example: '100' return '100'
    """
    res = val
    regex = r'\.\d0'
    if re.search(regex, val, flags = 0):
        #match = re.search(regex, val, flags = 0)
        #print 'match:{}'.format(match)
        if val[-1] == '0':
            res = val[:-1]
    return res

def trimspace_regex(val):
    """Trim the space after sign +/- if there is one in val
    val : string from rt-5100
    eg val = '+ 2,00'  --> return '+2.00'
    eg val ='  0,00'   --> return '  0.00'

    return the trimed string
    """
    regex=r'^[+-] ' # don't forget the space at the end of the regex
    if re.search(regex, val, flags = 0):
        #match = re.search(regex, val, flags = 0)
        #print 'match:{}'.format(match)
        val=val[:1]+val[2:]
    return val

def set2none(val):
    """Set val to None if val is equal to 0.00, 
    """
    regex=r'^0+\.0+$'
    if re.search(regex,val,flags=0):
        val=None
    return val


def get_values(filter):
    """Return a dictionnary of the values
    
        filter(str) : the letter from the interface manual rs-232 of RT-5100
        Il y a un probleme quand il n'y a aucune ligne qui correspond au filtre
        log_path : path to the file with the datas given by RT-5100 device
        
        values: eg : values:['OR', '- 2.75', '  0.00', '  0']
        
        morceaux : eg : ['2016-05-02T05:37:02.410503\t\x02', 'OR', '- 2.75', '  0.00', '  0', '\r\n']
        return : tuple .vals:({'cyl_od': '- 1.25', 'axe_od': '125', 'sph_od': '+ 5.50'}, {'sph_os': '+ 5.50', 'axe_os': '125', 'cyl_os': '- 1.25'})
    """
    coupures = [28, 30, 36, 42, 46] 
    filterR = filter+'R'
    filterL = filter+'L'
    log_path = os.path.join(os.path.expanduser('~'),'rt5100rs232','tmp.log')
    print 'log_path:{}'.format(log_path)
    if filter not in ['f','n','F','N','O']:
        print "print there is a problem with your filter:{}".format(filter)
        print "{} is not a code for RT-5100 datas".format(filter)
    else:
        try:
            file = open(log_path, 'r')
            for line in file.readlines():
                if line.find(filterR) != -1 or line.find(filterL) != -1:
                    morceaux = [line[i:j] for i, j in zip([0] + coupures, coupures + [None])] # on coupe les lignes en morceaux qui isolent les champs.
                    values=morceaux[1:5] # on élimine le champ date et on récupere que les champs datas.SCA dans une liste
                    # morceaux[2] --> sph 6 bits datas
                    # morceaux[3] --> cyl 6 bits datas
                    # morceaux[4] --> axes 6 bits datas
                    # morceaux[2:5] donne ['S','C','A']
                    # lets format the str to fit the odoo selection for SCA
                    print 'morceaux:{}'.format(morceaux)
                    print 'original values: {}'.format(values)
                    values=[val.strip() for val in values]
                    print 'values stripped:{}'.format(values)
                    values=[trimspace_regex(val) for val in values]
                    print 'values trimspace:{}'.format(values)
                    values=[trimzero(val) for val in values]
                    print 'values trimzero:{}'.format(values)
                    print 'formated values:{}'.format(values)
                    values=[set2none(val) for val in values]
                    print 'values set to None: {}'.format(values)
                    if values[0] == filterR: # On filtre pour l'oeil droit
                        valuesOD=dict(zip(keysOR,values[1:]))
                        if valuesOD['cyl_od'] == None:
                            valuesOD['axis_od']=None
                        print 'valuesOD:{}'.format(valuesOD)
                    else:
                        valuesOS=dict(zip(keysOS,values[1:])) #on filtre pour l'oeil gauche
                        if valuesOS['cyl_os'] == None:
                            valuesOS['axis_os']=None
                        print 'valuesOS:{}'.format(valuesOS)

        except IOError, (error, strerror):
            print "I/O Error(%s): %s" % (error, strerror)

    res=[valuesOD, valuesOS]
    print 'res:{}'.format(res)
    return res