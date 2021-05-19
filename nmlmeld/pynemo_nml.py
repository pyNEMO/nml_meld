'''
Created on Tue Oct 30 15:19:56 2018

Tool to compare and edit NEMO namelist files. 

@author James Harle

$Last commit on: Wed 19 May 2021$
'''

import re
import glob
import sys
import sip
try:
    QString = unicode
except NameError:
    # Python 3
    QString = str

sip.setapi('QString', 2)
from copy import deepcopy
from functools import partial 
import collections

from PyQt5.QtCore    import Qt, pyqtSlot, QCoreApplication
from PyQt5.QtWidgets import QApplication, QErrorMessage, QAbstractItemView, \
                            QPushButton, QToolButton, QLineEdit, QVBoxLayout, \
                            QTreeView, QComboBox, QDialog, QHBoxLayout, \
                            QFileDialog, QMessageBox, QHeaderView
from PyQt5.QtGui     import QStandardItem, QStandardItemModel, QColor

# TODO add a search box to focus only desired nam blocks

def compare(nlist_1, nlist_2, gui):
    
    if gui:
        app = QApplication(sys.argv)
        print(nlist_1) # TODO: At the moment nlist_1 is hard coded for a directory scan
        print(nlist_2)
        ex = TestDialog(nlist_1, nlist_2)
        ex.show()
        #accepted = ex.exec_()
        #if not accepted:
        #    return
        #data1 = deepcopy(ex.get_data1())
        #data2 = deepcopy(ex.get_data2())
        
        sys.exit(app.exec_())
    else:
        print('command line tool not yet configured')
        sys.exit()
        
class TestDialog(QDialog):
    def __init__(self, nlist_0, nlist_1):

        super(TestDialog, self).__init__()
        
        
        self.emsg = QErrorMessage(self)
        self.emsg.setWindowModality(Qt.WindowModal)
        self.emsg.children()[2].setVisible(False)
        
        data0=self.dir_scan(nlist_0,'*.f90')
        nl_1 = deepcopy(data0)
        data1=self.namelist_scan(nlist_1, nl_1)
        # TODO: need to make sure that all nam_block entries have same nam_items 
        
        cols = ['col0', 'col1']
                
        # Copy input data for manipulation
        self.data = {}
        self.data['col0'] = deepcopy(data0)
        self.data['col1'] = deepcopy(data1)
        
        # TreeView for each data set
        self.tree = {}
        for col in cols:
            self.tree[col] = QTreeView()
        
        # Layout
        btOk = QPushButton("OK")
        btCancel = QPushButton("Cancel")
        btSearch = QPushButton('Search')
        self.searchInput= QLineEdit()
        
        # Search Box
        self.searchInput.setText(QCoreApplication.translate(
                     "Find a nam_block or nam_item", "Enter search text here"))
        btSearch.setToolTip(
            QCoreApplication.translate(
                "Find a nam_block or nam_item", 
                "Enter search text here, press ENTER again to go to next match!"
            )
        )
        btSearch.clicked.connect(self.searchItem)
        
        
        # First row
        hbox1 = QHBoxLayout()
        hbox1.addStretch(1)
        hbox1.addWidget(btSearch, 100)
        #self.connect(self.btSearch, SIGNAL("returnPressed()"), self.searchItem)
        
        hbox1.addWidget(self.searchInput)
        #hbox1.addWidget(btSearch)
        hbox1.addWidget(btOk)
        hbox1.addWidget(btCancel)
        
        
        #self.button.clicked.connect(self.handleButton)
        
        # Second row
        hbox2 = QHBoxLayout()
        #hbox2.addStretch(1)
        for col in ['col0', 'col1']:
            hbox2.addWidget(self.tree[col])
        
        # Wrap both columns in a container
        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        #vbox.addWidget(self.tree1)
        self.setLayout(vbox)
        self.setGeometry(300, 300, 800, 400)

        # Button signals
        btCancel.clicked.connect(self.reject)
        btOk.clicked.connect(self.accept)

        # Tree view
        
        for col in cols:
            col_next = cols[1-cols.index(col)]
            self.tree[col].setModel(QStandardItemModel())
            self.tree[col].setAlternatingRowColors(True)
            #self.tree[col].model().setData(self.tree[col].model().index(1, 1), QtGui.QBrush(QtGui.QColor(255, 0, 0)), QtCore.Qt.BackgroundRole)
            self.tree[col].setSortingEnabled(True)
            self.tree[col].setHeaderHidden(False)
            #self.tree[col].setColumnWidth(2, 30) # This does work!
            self.tree[col].setSelectionBehavior(QAbstractItemView.SelectItems)
            self.tree[col].model().setHorizontalHeaderLabels(['Parameter', 'Value', 'Update'])
            self.tree[col].header().setSectionResizeMode(0, QHeaderView.Stretch)
            self.tree[col].header().setSectionResizeMode(1, QHeaderView.Stretch)
            self.tree[col].header().resizeSection(2, 50)
            self.tree[col].header().setSectionResizeMode(2, QHeaderView.Fixed)
            self.tree[col].header().setStretchLastSection(False)
            if col!='col0':
            #                self.tree[col].model().setHorizontalHeaderLabels(['Update', 'Parameter', 'Value'])
                self.tree[col].header().moveSection(2,0)
            #self.tree1.model().horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)


        for col in cols:        
            for x in self.data[col]:
                if not self.data[col][x]: # why did I write this in??
                    continue
                self._add_nam_block(x, col)
                
        for col in cols:
            col_next = cols[1-cols.index(col)]
            #self.tree[col].model().itemChanged.connect(partial(self.handleItemChanged, col))
            self.tree[col].expanded.connect(partial(self.handleExpanded, col, col_next))
            self.tree[col].collapsed.connect(partial(self.handleCollapsed, col, col_next))

            
        self.tree['col0'].verticalScrollBar().valueChanged.connect(
            self.tree['col1'].verticalScrollBar().setValue)
        self.tree['col1'].verticalScrollBar().valueChanged.connect(
            self.tree['col0'].verticalScrollBar().setValue)
        
        for col in cols:
            self.tree[col].model().itemChanged.connect(partial(self.handleItemChanged, col))

        #for col in cols:
        #    other = self.tree[col].model().findItems('nambdy', QtCore.Qt.MatchFixedString)
        #    newIndex=self.tree[col].model().indexFromItem(other[0])
        #    self.tree[col].scrollTo(newIndex, 3) # Centre
            
        # msg = QtWidgets.QMessageBox()
        # msg.setWindowModality(QtCore.Qt.WindowModal)
        # msg.setIcon(QtWidgets.QMessageBox.Critical)
        # msg.setText("Error")
        # msg.setInformativeText('More information')
        # msg.setWindowTitle("Error")
        # msg.exec_()
        
        #emsg.showMessage('Message: ')
        
        
    def _add_nam_block(self, nam_block, col):
        
        # TODO: run initial check on all the data to see if correct type
        
        # Set constants
        color_diff = QColor(205, 92,  92)
        color_miss = QColor( 92, 92, 205)
        
        # Which namelist are we dealing with
        if col=='col0': 
            col_alt = 'col1'
            arrow   = 4
        else:
            col_alt = 'col0'
            arrow   = 3
        
        # Local variables
        tree   = self.tree[col]
        model  = tree.model()
        nambk0 = self.data[col][nam_block]
        if nam_block in self.data[col_alt]:
            nambk1 = self.data[col_alt][nam_block]
        else:
            nambk1 = False
                
        # Add namelist block
        parent0 = QStandardItem(nam_block)  # Namelist header
        parent1 = QStandardItem()           # Not used
        parent2 = QStandardItem()           # Placeholder for QToolButton
        
        parent0.setFlags(Qt.NoItemFlags)
        parent1.setFlags(Qt.NoItemFlags)
             
        # Add row
        model.appendRow([parent0, parent1, parent2])
        
        parind0 = parent0.index()
        parind2 = parent2.index()

        # Add widget to handle the transfer of nam_block 
        if not nambk1 or (nambk0 != nambk1): 
            q_btn = QToolButton()
            #q_btn.setText(arrow)
            q_btn.setArrowType(arrow)
            q_btn.clicked.connect(partial(self.pass_block, parind0, col))
            tree.setIndexWidget(parind2, q_btn)
            
        if not nambk1:
            model.setData(parind0, color_miss, Qt.ForegroundRole)
        elif (nambk0 != nambk1):
            model.setData(parind0, color_diff, Qt.ForegroundRole)

#parent_item.setData("this is a parent", QtCore.Qt.ToolTipRole)

        # Add namelist item within block
        for nam_item in nambk0:
            
            # Retrieve value of namelist variable
            nam_val0 = nambk0[nam_item]
            
            # If nam_block exists in other namelist
            if nambk1:
                # TODO: temp fix is item isn't present
                if nam_item in nambk1:
                    nam_val1 = nambk1[nam_item]
                else:
                    nam_val1 = None
                    
            child0  = QStandardItem(nam_item)
            child1  = QStandardItem(str(nam_val0)) #TODO: rm quotes from cn_
            child2  = QStandardItem()
            
            #child0.setFlags(QtCore.Qt.NoItemFlags | 
           #                 QtCore.Qt.ItemIsEnabled)
            child0.setFlags(Qt.NoItemFlags )
            
            child1.setFlags(Qt.ItemIsEnabled |
                            Qt.ItemIsEditable |
                          ~ Qt.ItemIsSelectable)            
            
            parent0.appendRow([child0, child1, child2])
                  
            chiind0 = child0.index()
            chiind1 = child1.index()
            chiind2 = child2.index()
            
            
            # If bool then replace box with drop down
            if nam_item[0:2]=='ln':
                c_box = QComboBox()
                c_box.addItem('None')
                c_box.addItem('.true.')
                c_box.addItem('.false.')
                ind = c_box.findText(str(nam_val0), Qt.MatchFixedString)
                c_box.setCurrentIndex(ind)
                tree.setIndexWidget(chiind1, c_box)

            #TODO: maybe add arrows to all, just toggle visibility
            if nambk1 and (nam_val0 != nam_val1):
                q_btn = QToolButton()
                
                #q_btn.setText(arrow)
                q_btn.clicked.connect(partial(self.pass_entry, col, nam_block, 
                                                                    nam_item ))
                q_btn.setArrowType(arrow)
                #q_btn.setEnabled(True)
                tree.setIndexWidget(chiind2, q_btn)
                
                
                model.setData(chiind0, color_diff, Qt.ForegroundRole)
            elif not nambk1:
                model.setData(chiind0, color_miss, Qt.ForegroundRole)
            else:
                q_btn = QToolButton()
                
                #q_btn.setText(arrow)
                q_btn.clicked.connect(partial(self.pass_entry, col, nam_block, 
                                                                    nam_item ))
                q_btn.setArrowType(0)
                q_btn.setEnabled(False)
                tree.setIndexWidget(chiind2, q_btn)
                    
    def handleItemChanged(self, col, item):
        

        if col=='col0': 
            col_alt = 'col1'
        else:
            col_alt = 'col0'
            
        tree   = self.tree[col]
        model  = tree.model()
        #print(help(model.match))
        print('here****************** item changed')
        if item.parent() is None:
            print('Parent')
        else:
            parent = self.data[col][item.parent().text()]
            p2 = self.data[col_alt][item.parent().text()]
            
            nam_block = item.parent().text()

            nam_item  = item.parent().child(item.row(), 0).text()
            
            item_type = nam_block[0:2]
            item_val  = item.text() # same a nam_item!

            print(type(item_val))

#app = QtWidgets.QApplication([])

#error_dialog = QtWidgets.QErrorMessage()
#error_dialog.showMessage('Oh no!')

#app.exec_()
            print('headline   '+nam_block+' '+nam_item+' '+item_val+' ')
            
            
            # TODO check item.text is right type or None
            # if it is do
            #parent[nam_block] = type(item.text())(item.text())
        
            # else keep the original value and flag somehow
            color_chng = QColor(0, 0,  0)
            color_chn1 = QColor(176, 176,  176)
            Index=model.indexFromItem(item)

            color_diff = QColor(205, 92,  92)
            color_test = QColor(100, 0,  92)
       
            print('whos the daddy'+item.parent().text())
            
            
            
            
            
            
            if nam_item != item_val: # need to work out how/why to stop the itemchanged call when colors are updated
                
                self.data[col][nam_block][nam_item]=item_val
                
                self.color_update(col,nam_block, nam_item)
                
            # TODO error check with pop up if the value isn't compatible with the key
        
    def handleExpanded(self,  col, col_next, idx):

        item = self.tree[col].model().itemFromIndex(idx)
        text = item.text()
        for other in self.tree[col_next].model().findItems(text, Qt.MatchFixedString):
            newIndex=self.tree[col_next].model().indexFromItem(other)
            self.tree[col_next].setExpanded(newIndex, True)

    def handleCollapsed(self, col, col_next, idx):
        item = self.tree[col].model().itemFromIndex(idx)
        text = item.text()
        for other in self.tree[col_next].model().findItems(text, Qt.MatchFixedString):
            newIndex=self.tree[col_next].model().indexFromItem(other)
            self.tree[col_next].setExpanded(newIndex, False)
        
    def get_data1(self):
        return self.data1

    def get_data2(self):
        return self.data2

    def pass_block(self, ind, col, idx):
        
        if col=='col0': 
            col_alt = 'col1'
        else:
            col_alt = 'col0'
            
        tree   = self.tree[col]
        model  = tree.model()
        
        #item = model.itemFromIndex(idx)
        
        #nam_block = item.parent().child(item.row(), 0).text()
        
        #print(ind, idx)
        nam_block = model.itemFromIndex(ind).text()
        print(model.itemFromIndex(ind).text())
        
        # Map changes in the data
        self.data[col_alt][nam_block] = self.data[col][nam_block]
        
        for other in self.tree[col_alt].model().findItems(nam_block, Qt.MatchFixedString | Qt.MatchRecursive):
            for cnt in range(other.rowCount()):
                nam_item = other.child(cnt,0).text()
                other.child(cnt,1).setText(str(self.data[col][nam_block][nam_item]))
                    
                    
        #self.secondColumn.parameter.setText(self)
        # item = self.tree['col0'].model().itemFromIndex(idx)
        # text = item.text()
        # for other in self.tree2.model().findItems(text, QtCore.Qt.MatchFixedString):
        #     newIndex=self.tree2.model().indexFromItem(other)
            # code to update value in column two

    def pass_entry(self, col, nam_block, nam_item, idx):
        

        #buttonClicked = self.sender()
        #postitionOfWidget = buttonClicked.pos()
        #print(postitionOfWidget)
        #print(dir(sending_button))
        #print(str(sending_button.objectName()))

            
        if col=='col0': 
            col_alt = 'col1'
        else:
            col_alt = 'col0'
            
            
        tree   = self.tree[col]
        model  = tree.model()
        parent = self.data[col][nam_block]
        p2 = self.data[col_alt][nam_block]
            
           # nam_block = item.parent().text()

           # nam_item  = item.parent().child(item.row(), 0).text()
            
           # item_type = nam_block[0:2]
           # item_val  = item.text() # same a nam_item!
            
        #sender = self.sender()
        print(col, nam_block, nam_item, idx)
        print(self.data[col_alt][nam_block][nam_item])
        print(self.data[col][nam_block][nam_item])
        self.data[col_alt][nam_block][nam_item] = self.data[col][nam_block][nam_item]
        
        
        for other in self.tree[col_alt].model().findItems(nam_block, Qt.MatchFixedString | Qt.MatchRecursive):
            print('$$$$$$$$$$$$$$$$$$')
            print(other.child(0,0).text())
            print(range(other.rowCount()))
            print(nam_item)
            for cnt in range(other.rowCount()):
                blk = other.child(cnt,0).text()
                if blk == nam_item:
                    print('@@@@@@@@@@@@@@@@@ found it')
                    print(other.child(cnt,0))
                    print(other.child(cnt,1))
                    other.child(cnt,1).setText(str(self.data[col][nam_block][nam_item]))
            
            #item.parent().child(item.row(), 0).text()
            
            
           # print(other.takeRow(0)[0].text()    )
            
           # print(dir(other.takeRow(0)[0]))
            
        
        
        # TODO: do I need this as handleItemChanged maybe triggered anyway?
        self.color_update(col,nam_block, nam_item)
            
            
    def color_update(self,col,nam_block, nam_item):
        
        color_chng = QColor(0, 0,  0)
        color_chn1 = QColor(176, 176,  176)
       
        color_diff = QColor(205, 92,  92)
        color_test = QColor(100, 0,  92)
        
        if col=='col0': 
            col_alt = 'col1'
        else:
            col_alt = 'col0'
            
            
        tree   = self.tree[col]
        model  = tree.model()
        parent = self.data[col][nam_block]
        p2 = self.data[col_alt][nam_block]
        
        
        for other in self.tree[col_alt].model().findItems(nam_item, Qt.MatchFixedString | Qt.MatchRecursive):
            newIndex=self.tree[col_alt].model().indexFromItem(other)
        #    print('NEWINDEX')
       #     print(newIndex.row())
        #    print(newIndex.column())
       #     print(dir(newIndex))
            #TODO: sort out indexing
       #     self.tree[col_alt].model().setData(newIndex,str(self.data[col][nam_block][nam_item]),Qt.DisplayRole)
            if p2[nam_item] != parent[nam_item]:
                print('tttttttttttttttesting1a')
                print(p2[nam_item])
                print(parent[nam_item])
                print('****************Not equal1')
                self.tree[col_alt].model().setData(newIndex, color_diff, Qt.ForegroundRole)
                #TODO: insert arrow
            else:
                print('tttttttttttttttesting1b')
                print(p2[nam_item])
                print(parent[nam_item])
                print('****************equal1')
                self.tree[col_alt].model().setData(newIndex, color_chng, Qt.ForegroundRole)
                #TODO: remove arrow
                
  #              q_btn = item.parent().child(item.row(), 2)
  #              print(dir(item.parent()))
   #             print(item.parent().text())
   #             print(dir(item.parent().child(item.row(), 2)))
   #             print(item.parent().child(item.row(), 2).hasChildren())
                #q_btn = item.parent().child(item.row(), 2)
                #q_btn.data.setArrowType(0)
                #q_btn.setEnabled(False)

        # TODO: probably don't need the following for block
        for other in self.tree[col].model().findItems(nam_item, Qt.MatchFixedString | Qt.MatchRecursive):
            
            newI=self.tree[col].model().indexFromItem(other)
            print("We're in Row")
            print(newI.row())
        #other = self.tree['col1'].model().findItems(p2[nam_item], Qt.MatchFixedString)
        #print(item)
        #newIndex=self.tree['col1'].model().indexFromItem(item)

            #if p2[nam_item] != parent[nam_item]:
            if p2[nam_item] != parent[nam_item]:
                print('tttttttttttttttesting2a')
                print(p2[nam_item])
                print(parent[nam_item])
                print('****************Not equal0')
                self.tree[col].model().setData(newI, color_diff, Qt.ForegroundRole)
            else:
                print('tttttttttttttttesting2b')
                print(p2[nam_item])
                print(parent[nam_item])
                print('****************equal0')
                self.tree[col].model().setData(newI, color_chng, Qt.ForegroundRole)
                #TODO: insert arrow
            
        pi0 = self.tree[col].model().findItems(nam_block, Qt.MatchFixedString) 
        pi1 = self.tree[col_alt].model().findItems(nam_block, Qt.MatchFixedString)
        in0 =self.tree[col].model().indexFromItem(pi0[0])
        in1 =self.tree[col_alt].model().indexFromItem(pi1[0])    
        
        if self.data[col][nam_block] != self.data[col_alt][nam_block]:

            self.tree[col].model().setData(in0, color_diff, Qt.ForegroundRole)
            self.tree[col_alt].model().setData(in1, color_diff, Qt.ForegroundRole)
        else:
            self.tree[col].model().setData(in0, color_chn1, Qt.ForegroundRole)
            self.tree[col_alt].model().setData(in1, color_chn1, Qt.ForegroundRole)   
                    
                      
        # TODO check item.text is right type or None
        # if it is do
        #parent[key] = type(item.text())(item.text())
        #self.secondColumn.parameter().setText(self)
        #item = self.tree1.model().itemFromIndex(idx)
        #text = item.text()         
        #for other in self.tree2.model().findItems(text, QtCore.Qt.MatchFixedString):
        #    newIndex=self.tree2.model().indexFromItem(other)
            # code to update value in column two
            
            
    def searchItem(self):
        """execute the search and highlight the (next) result"""
        txt = str(self.searchInput.text())
        if txt != self.searchText:
            self.searchText = txt
            tmp = self.model.findItems(
                txt, Qt.MatchFixedString | Qt.MatchContains | Qt.MatchWildcard | Qt.MatchRecursive
            )
            self.searchList = [i.index() for i in tmp]
        if self.searchList:
            mi = self.searchList.pop()
            self.treeView.setCurrentIndex(mi)
            self.treeView.expand(mi)
            self.treeView.scrollTo(mi)
        else:
            QMessageBox.information(
                self,
                QCoreApplication.translate("DataStorageBrowser", "No (more) matches!"),
                QCoreApplication.translate(
                    "DataStorageBrowser", "No (more) matches found! Change you search text and try again!"
                ),
            )
            self.searchText = ""
            
    '''
    file picker call back for output file input field
    '''
    @pyqtSlot()
    def get_fname(self):
        # When you call getOpenFileName, a file picker dialog is created
        # and if the user selects a file, it's path is returned, and if not
        # (ie, the user cancels the operation) None is returned
        fname = QFileDialog.getSaveFileName(self, 'Select output file', '', selectedFilter='*.ncml')[0]
        if fname:
            self.filename = fname #returns a QString
            self.top_outfile_name.setText(str(fname))
            #print 'the output file is set to : ' + self.filename

    def dir_scan(self,bld_dir,ftype):
        """ 
        Scan directory for namelist variables

        Scans the BLD directory in a NEMO configuration directory and
        returns a dictionary of dictionaries of namelist variables.

        Args:
            bld_dir         (str)  : BLD directory from a NEMO cfg diretcory
            ftype           (str)  : file type e.g. *.f90 (inactive)
            
        Returns:
            nl              (dict) : a dictionary of all the namelist variables
        """
        
        pattern=re.compile('NAMELIST')
        nl     = {}
        
        f90_files = glob.glob(bld_dir+'*.f90') # need to update to make recursive
        
        f90_files=glob.glob(bld_dir+'/**/*.[F,f]90', recursive=True)
        
        for fname in f90_files:
            for i, line in enumerate(open(fname, errors='ignore')):
                if re.search(pattern,line): # replace as NAMELIST only occurs once
                    #print(pattern, line)
                    nl_sub = collections.OrderedDict()
                    if "&" in line:
                        l=line.rsplit('&')[0].strip()
                        count = i+1
                        while l[-1]==',':
                            nxt = [x for j, x in enumerate(open(fname)) if j in [count,]][0]
                            if nxt.count('&')>=1 and nxt.strip()[0]=='&': 
                                l=l+' '+nxt.rsplit('&')[1].strip()
                            elif nxt.count('&')==1 :
                                l=l+' '+nxt.rsplit('&')[0].strip()
                            else:
                                l=l+' '+nxt.strip()
                                # need to print('error') # proper handling of errors please
                            count+=1
                    nam_name  = l.rsplit('/')[1].strip()
                    nam_items = l.rsplit('/')[2].strip()
                    nam_items = nam_items.rsplit('!')[0].strip()
                    nam_items = nam_items.rsplit(',')
                
                    for n in range(len(nam_items)):
                        nl_sub[nam_items[n].strip()] = None
                      
                    # need a check in here to make sure that all identical namelists have the same number of entries?
                    nl[nam_name]=nl_sub
                    
        return nl
  
    def namelist_scan(self,namelist_in, nl_dict):
        """ 
        Scan a namelist and populates the namelist dictionary.

        Scans the input namelist and populates a dictionary of dictionaries 
        derived from the NEMO source code. 

        Args:
            namelist_in     (str)  : BLD directory from a NEMO cfg diretcory
            nlist_dict_in   (str)  : file type e.g. *.f90 (inactive)
            
        Returns:
            nlist_d         (dict) : a dictionary of populated namelist vars
        """
        
        nam_name = None
        nam_item = None
    
        pattern=re.compile('&nam')
        
        for i, line in enumerate(open(namelist_in)):
            if len(line.strip()) > 0 :
                if re.search(pattern,line):  
                    nam_name  = line.rsplit()[0].strip()[1:]
                elif line.strip()[0] != '!' and line.strip()[0] != '/':
                    nam_item  = line.rsplit()[0].strip()
                    nam_val   = line.rsplit()[2].strip()
                if nl_dict.get(nam_name) != None and nam_item != None:
                    nl_dict[nam_name][nam_item] = nam_val # remember we may be adding new nam_vals here so need to check later
                    #print 'A:'+nam_name+': '+nam_item+' : '+nam_val
                elif nam_name != None and nam_item != None:
                    nl_dict[nam_name]={}
                    nl_dict[nam_name][nam_item] = nam_val
                    #print 'B:'+nam_name+': '+nam_item+' : '+nam_val
                nam_item = None
            
            
        return nl_dict   
    
    def namelist_write(self,namelist_out):
        """ 
        Scan a namelist and populates the namelist dictionary.

        Scans the input namelist and populates a dictionary of dictionaries 
        derived from the NEMO source code. 

        Args:
            namelist_in     (str)  : BLD directory from a NEMO cfg diretcory
            nlist_dict_in   (str)  : file type e.g. *.f90 (inactive)
            
        Returns:
            nlist_d         (dict) : a dictionary of populated namelist vars
        """

    def item_type(self,i):

        item_switcher={
            'ln': bool,
            'nn': int,
            'rn': float,
            'cn': str,
            'sn': str}
            
        return item_switcher.get(i, self.emsg.showMessage('Message:'))

class Other(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return '(%s, %s)' % (self.x, self.y)
    
    
    
#     user_input = input("Enter your Age ")

# print("\n")
# try:
#     val = int(user_input)
#     print("Input is an integer number. Number = ", val)
# except ValueError:
#     try:
#         val = float(user_input)
#         print("Input is a float  number. Number = ", val)
#     except ValueError:
#         print("No.. input is not a number. It's a string")



        
    

