from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pymssql
import _mssql
import pymysql
import numpy as np
import pandas as pd
import sys
import datetime
import time
from bcrypt import _bcrypt
import bcrypt
import re
import hashlib
import requests
import datetime
import win32com.client
import os
import _cffi_backend
from pandas.io.excel import ExcelWriter

'''
产线问题处理系统

'''





class WinMain(QMainWindow):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		tabwidget=QTabWidget()
		self.winnofinish=WinNoFinish()
		# self.winfinish=WinFinish()
		# self.wincrafts=WinCrafts()
		tabwidget.addTab(self.winnofinish,'问题记录')
		# tabwidget.addTab(self.winfinish,'已完成')
		# tabwidget.addTab(self.wincrafts,'工艺有变更')
		self.setCentralWidget(tabwidget)
		self.show()
		self.setWindowTitle('问题记录'+version)

'''
显示所有未完成问题
修改为显示全部问题，添加筛选功能
'''
class WinNoFinish(QWidget):
	def __init__(self):
		super().__init__()
		self.df=None
		self.dic={}
		# self.columns=['id','流水号','计划号','型号','系列号','批次','计划数量','异常情况','问题分类',\
		# 	'发生时间','提交人','提交时间','指定负责人','原因分析状态','分析人','分析质检确认人','方案解决状态','方案给出人',\
		# 	'是否变更长期文件','文件变更负责人','最终状态']

		# self.columns=['id','型号','异常情况','原因分析','解决方案','原因分析状态','方案解决状态','最终状态','计划完成状态',\
		# 	'分析人','分析质检确认人','方案给出人','指定负责人','问题提交人','责任部门','发生时间','提交时间',\
		# 	'流水号','计划号','系列号','批次','计划数量','问题分类',\
		# 	'是否变更长期文件','文件变更负责人']

		self.columns=['id','型号','异常情况','影响范围','现象分类','原因分析','解决方案','原因分析状态',\
			'方案解决状态','最终状态','计划完成状态','原因分类',\
			'分析人','分析质检确认人','方案给出人','指定负责人1','指定负责人2','问题提交人','责任部门',\
			'发生时间','影响结束时间','提交时间',\
			'流水号','计划号','系列号','批次','计划数量',\
			'是否变更长期文件','文件变更负责人','退回状态','退回说明','标记']

		self.initUI()

	def initUI(self):
		btn_flush=QPushButton('刷新',self)
		btn_flush.clicked.connect(self.flush_event)
		btn_export=QPushButton('输出excel',self)
		btn_export.clicked.connect(self.export_event)
		check_filter=QCheckBox('筛选',self)
		check_filter.setCheckState(0)
		check_filter.stateChanged.connect(self.check_filter_event)

		label_date_start=QLabel('开始日期(含)',self)
		label_date_end=QLabel('结束日期(含)',self)
		self.date_edit_start=QDateEdit(QDate.currentDate(),self)
		self.date_edit_end=QDateEdit(QDate.currentDate(),self)

		self.table=QTableWidget(0,32,self)
		self.table.setHorizontalHeaderLabels(self.columns)
		self.table.cellDoubleClicked.connect(self.table_double_clicked_event)
		self.table.cellClicked.connect(self.table_clicked_event)
		# self.table.horizontalHeader().sectionClicked.connect(self.headerclicked)

		btn_add=QPushButton('添加异常记录',self)
		btn_add.clicked.connect(self.add_event)

		action_delete_record=QAction('删除',self)
		action_delete_record.triggered.connect(self.delete_record)
		action_add_finish_time=QAction('添加影响结束时间',self)
		action_add_finish_time.triggered.connect(self.add_finish_time)
		action_delete=QAction('变更指定负责人',self)
		action_delete.triggered.connect(self.modify_duty_person)
		action_finish=QAction('完结该记录',self)
		action_finish.triggered.connect(self.finish_record)
		
		action_add_type=QAction('添加问题分类',self)
		action_add_type.triggered.connect(self.add_type)
		action_finish_crafts=QAction('完结变更长期文件',self)
		action_finish_crafts.triggered.connect(self.finish_crafts)
		action_modify_crafts=QAction('修改变更文件负责人',self)
		action_modify_crafts.triggered.connect(self.modify_crafts_event)
		action_modify_duty=QAction('指定负责人移交',self)
		action_modify_duty.triggered.connect(self.modify_duty_person_again)


		'''退回及标记'''
		action_back=QAction('退回',self)
		action_back.triggered.connect(self.action_back)
		action_back_cancel=QAction('退回恢复',self)
		action_back_cancel.triggered.connect(self.action_back_cancel)
		action_mark=QAction('标记',self)
		action_mark.triggered.connect(self.action_mark)
		# action_mark_cancel=QAction('取消标记',self)
		# action_mark_cancel.triggered.connect(self.action_mark_cancel)


		self.table.addAction(action_add_finish_time)
		self.table.addAction(action_delete)
		self.table.addAction(action_modify_duty)
		self.table.addAction(action_finish)
	

		self.table.addAction(action_add_type)
		self.table.addAction(action_finish_crafts)
		self.table.addAction(action_modify_crafts)
		self.table.addAction(action_delete_record)


		self.table.addAction(action_back)
		self.table.addAction(action_back_cancel)
		self.table.addAction(action_mark)
		# self.table.addAction(action_mark_cancel)


		self.table.setContextMenuPolicy(Qt.ActionsContextMenu)
		hlayout_t=QHBoxLayout()
		hlayout_t.addWidget(btn_add,alignment=Qt.AlignLeft)
		hlayout_t.addWidget(label_date_start,alignment=Qt.AlignRight)
		hlayout_t.addWidget(self.date_edit_start)
		hlayout_t.addWidget(label_date_end,alignment=Qt.AlignRight)
		hlayout_t.addWidget(self.date_edit_end)
		hlayout_t.addWidget(check_filter,alignment=Qt.AlignCenter)
		hlayout_t.addWidget(btn_export,alignment=Qt.AlignRight)
		hlayout_t.addWidget(btn_flush,alignment=Qt.AlignRight)

		# hlayout_b=QHBoxLayout()
		# hlayout_b.addWidget(btn_add,alignment=Qt.AlignRight)

		vlayout=QVBoxLayout(self)
		vlayout.addLayout(hlayout_t)
		vlayout.addWidget(self.table)
		# vlayout.addLayout(hlayout_b)

		self.setLayout(vlayout)
		self.show()

	def action_back(self):
		print('退回函数')
		record_id=self.table.item(self.table.currentRow(),0).text()
		cur.execute("select duty_person,plan_state,solve_state from problem.problem_record where id=%s",(record_id))
		li=cur.fetchall()
		conn.commit()

		if li[0][1]!='待处理' or li[0][2]!='待处理':
			QMessageBox(text='   已分析或已给出解决方案，不可退回！  ',parent=self).show()
			return

		duty_person=li[0][0].replace(' ','')
		if duty_person=='':
			return

		login_flag,name=WinConfirm(duty_person).get_result()
		if login_flag=='fail':
			return

		self.win_back=WinBack(record_id,self.table)


	def action_back_cancel(self):
		record_id=self.table.item(self.table.currentRow(),0).text()
		cur.execute("select person from problem.problem_record where id=%s",(record_id))
		li=cur.fetchall()
		conn.commit()
		person=li[0][0].replace(' ','')
		if person=='':
			return

		login_flag,name=WinConfirm(person).get_result()
		if login_flag=='fail':
			return

		cur.execute("update problem.problem_record set back_flag='取消退回' where id=%s",(record_id))
		conn.commit()
		self.table.item(self.table.currentRow(),29).setText('取消退回')

		for i in range(self.table.columnCount()):
			self.table.item(self.table.currentRow(),i).setBackground(QBrush(QColor(255,255,255)))

	def action_mark(self):
		record_id=self.table.item(self.table.currentRow(),0).text()
		cur.execute("select name from problem.mark_person")
		li=cur.fetchall()
		mark_person=li[0][0]

		login_flag,name=WinConfirm(mark_person).get_result()
		if login_flag=='fail':
			return
		# cur.execute("update problem.problem_record set mark='标记' where id=%s",(record_id))
		# conn.commit()
		# self.table.item(self.table.currentRow(),31).setText('已标记')
		self.win_mark=WinMark(record_id,self.table)



	# def action_mark_cancel(self):
	# 	record_id=self.table.item(self.table.currentRow(),0).text()
	# 	cur.execute("select name from problem.mark_person")
	# 	li=cur.fetchall()
	# 	mark_person=li[0][0]

	# 	login_flag,name=WinConfirm(mark_person).get_result()
	# 	if login_flag=='fail':
	# 		return
	# 	cur.execute("update problem.problem_record set mark='标记取消' where id=%s",(record_id))
	# 	conn.commit()
	# 	self.table.item(self.table.currentRow(),31).setText('标记取消')


		
	def add_finish_time(self):
		record_id=self.table.item(self.table.currentRow(),0).text()
		cur.execute("select person from problem.problem_record where id=%s",(record_id))
		li=cur.fetchall()[0]
		login_flag,name=WinConfirm(li[0]).get_result()
		if login_flag=='fail':
			return
		self.win_add_finish_date=WinAddFinishDate(self.table.currentRow(),record_id,self)

	def delete_record(self):
		record_id=self.table.item(self.table.currentRow(),0).text()
		delete_time=datetime.datetime.now()
		delete_time=str(delete_time)[0:19]
		cur.execute("select main_model,project_id,model,batch_num,project_count,person,happen_time,\
			descript,commit_time,flow_num,plan_state,solve_state,finish_state,duty_person,problem_type,\
			duty_person2,stop_produce,problem_type2 from problem.problem_record where id=%s",(record_id))
		li=cur.fetchall()[0]


		if li[10]!='待处理' or li[11]!='待处理':
			QMessageBox(text='   已分析或已给出解决方案，不可删除！  ',parent=self).show()
			return

		login_flag,name=WinConfirm(li[5]).get_result()
		if login_flag=='fail':
			return


		cur.execute("insert into problem.problem_record_delete (main_model,project_id,model,batch_num,\
			project_count,person,happen_time,descript,commit_time,flow_num,plan_state,solve_state,\
			finish_state,duty_person,problem_type,duty_person2,stop_produce,problem_type2,delete_time) \
			values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",\
			(li[0],li[1],li[2],li[3],li[4],li[5],li[6],li[7],li[8],li[9],li[10],li[11],li[12],li[13],li[14],\
				li[15],li[16],li[17],delete_time))
		cur.execute("delete from problem.problem_record where id=%s",(record_id))
		conn.commit()
		self.table.removeRow(self.table.currentRow())

	def modify_crafts_event(self):
		record_id=self.table.item(self.table.currentRow(),0).text()
		cur.execute("select crafts_state from problem.solve_plan where problem_id=%s and plan_state='最新记录'",(record_id))
		li=cur.fetchall()
		if len(li)!=1:
			return
		flag=li[0][0]
		if flag != '变更':
			return

		cur.execute("select crafts_person from problem.solve_plan where problem_id=%s and plan_state='最新记录'",(record_id))
		li=cur.fetchall()	
		duty_person=li[0][0]
		
		cur.execute("select confirm_person from problem.solve_person where plan_id in (select id \
				from problem.solve_plan where problem_id=%s and plan_state='最新记录')",(record_id))
		li=cur.fetchall()
		li_solve_person=[]
		for i in li:
			li_solve_person.append(i[0])
		for i in li_solve_person:
			login_flag,name=WinConfirm(i).get_result()
			if login_flag=='fail':
				return
		login_flag_a,name_a=WinModifyDutyPerson(duty_person).get_result()
		print(login_flag_a,name_a)
		if login_flag_a=='fail':
			return
		if name=='':
			return
		cur.execute("update problem.solve_plan set crafts_person=%s where  problem_id=%s and \
			plan_state='最新记录'",(name_a,record_id))
		conn.commit()
		QMessageBox(text='   修改成功！  ',parent=self).show()
		self.flush_event()

	def export_event(self):
		li_df=[]
		for i in range(self.table.rowCount()):
			li_temp=[]
			for j in range(self.table.columnCount()):
				li_temp.append(self.table.item(i,j).text())
			li_df.append(li_temp)
		df=pd.DataFrame(li_df,columns=self.columns)

		li_hour=[]
		for i in range(self.table.rowCount()):
			pro_id=self.table.item(i,0).text()

			cur.execute("select p.flow_num,p.project_id,w.line_name,w.effect_date,w.workhour_manage,\
				w.workhour_technology,w.workhour_operate,w.confirm_person from problem.problem_record as p \
				right join problem.work_hour as w on p.id=w.problem_id where p.id=%s",(pro_id))

			li=cur.fetchall()
			li=list(li)
			print(li)
			li_hour=li_hour+li

		df_hour=pd.DataFrame(li_hour,columns=['流水号','计划id','线别','影响日期','管理工时','技术工时','操作工时'\
			,'确认人'])



		filename=QFileDialog.getSaveFileName(self,'存储为','D:/问题记录','xlsx')

		if filename[0]=='':
			return
		writer = ExcelWriter(filename[0]+'.'+filename[1])
		df.to_excel(writer,sheet_name='问题详情')
		df_hour.to_excel(writer,sheet_name='工时')
		writer.save()

	def headerclicked(self,index):
		self.winselectfilter=WinSelectFilter(self.df,self.columns,index,self.dic,self.table)

	def check_filter_event(self,state):
		if state==0:
			self.table.horizontalHeader().sectionClicked.disconnect(self.headerclicked)
			self.flush_event()
		if state==2:
			self.table.horizontalHeader().sectionClicked.connect(self.headerclicked)

	def table_clicked_event(self,row,column):
		print(self.table.horizontalHeaderItem(column).text())
		# self.table.horizontalHeaderItem(column).setBackground(QBrush(QColor(10,50,210)))
		# self.table.horizontalHeaderItem(column).setText(self.table.horizontalHeaderItem(column).text()+'=_=')
	def finish_crafts(self):
		record_id=self.table.item(self.table.currentRow(),0).text()
		cur.execute("select crafts_person from problem.solve_plan where problem_id=%s and plan_state='最新记录'",(record_id))
		li=cur.fetchall()
		if len(li)!=1:
			return
		duty_person=li[0][0]
		if duty_person=='':
			return
		login_flag,name=WinConfirm(duty_person).get_result()
		if login_flag=='fail':
			return
		cur.execute("update problem.solve_plan set crafts_state='已完成' \
			where problem_id=%s and plan_state='最新记录'",(record_id))
		conn.commit()
		self.flush_event()



	def finish_record(self):
		record_id=self.table.item(self.table.currentRow(),0).text()
		# duty_person=self.table.item(self.table.currentRow(),12).text()
		cur.execute("select finish_state from problem.problem_record where id=%s",(record_id))
		li=cur.fetchall()
		finish_state=li[0][0]
		if finish_state=='已完成':
			return
		cur.execute("select name from problem.finish_person")
		name=cur.fetchall()[0][0]
		login_flag,name=WinConfirm(name).get_result()
		if login_flag=='fail':
			return
		cur.execute("select plan_state,solve_state from problem.problem_record where id=%s",(record_id))
		li=cur.fetchall()
		old_plan_state=li[0][0]
		old_solve_state=li[0][1]
		if old_plan_state=='已分析':
			plan_state='已完成'
		if old_plan_state=='待处理':
			plan_state='无分析'
		if old_plan_state=='原因待查':
			plan_state='未完成'
		if old_plan_state=='已完成':
			plan_state='已完成'
		if old_solve_state=='已解决':
			solve_state='已完成'
		if old_solve_state=='待处理':
			solve_state='无解决方案'
		if old_solve_state=='已完成':
			solve_state='已完成'

		cur.execute("update problem.problem_record set plan_state=%s,solve_state=%s,\
			finish_state='已完成' where id=%s",(plan_state,solve_state,record_id))
		conn.commit()
		self.table.setItem(self.table.currentRow(),7,QTableWidgetItem(plan_state))
		self.table.setItem(self.table.currentRow(),8,QTableWidgetItem(solve_state))
		self.table.setItem(self.table.currentRow(),9,QTableWidgetItem('已完成'))
		# self.flush_event()

	def modify_duty_person(self):
		record_id=self.table.item(self.table.currentRow(),0).text()
		cur.execute("select duty_person,person from problem.problem_record where id=%s",(record_id))
		li=cur.fetchall()
		duty_person=li[0][0]
		commit_person=li[0][1]
		
		login_flag,name=WinConfirm(commit_person).get_result()
		if login_flag=='fail':
			return
		login_flag_a,name_a=WinModifyDutyPerson(duty_person).get_result()
		print(login_flag_a,name_a)
		if login_flag_a=='fail':
			return
		if name=='':
			return
		cur.execute("update problem.problem_record set duty_person=%s where id=%s",(name_a,record_id))
		conn.commit()
		QMessageBox(text='   修改成功！  ',parent=self).show()
												#!!!!
		self.table.item(self.table.currentRow(),15).setText(str(name_a))

	def modify_duty_person_again(self):
		record_id=self.table.item(self.table.currentRow(),0).text()
		cur.execute("select duty_person,duty_person2 from problem.problem_record where id=%s",(record_id))
		li=cur.fetchall()
		duty_person=li[0][1]
		commit_person=li[0][0]
		
		login_flag,name=WinConfirm(commit_person).get_result()
		if login_flag=='fail':
			return
		login_flag_a,name_a=WinModifyDutyPerson(duty_person).get_result()
		print(login_flag_a,name_a)
		if login_flag_a=='fail':
			return
		if name=='':
			return
		cur.execute("update problem.problem_record set duty_person2=%s where id=%s",(name_a,record_id))
		conn.commit()
		QMessageBox(text='   修改成功！  ',parent=self).show()
												#!!!!
		self.table.item(self.table.currentRow(),16).setText(str(name_a))


	def flush_event(self):
		s1=self.date_edit_start.date().toString("yyyy-MM-dd")
		s2=self.date_edit_end.date().addDays(1).toString("yyyy-MM-dd")
		# cur.execute("select id,flow_num,project_id,main_model,model,batch_num,project_count,descript,problem_type,happen_time,\
		# 	person,commit_time,duty_person,plan_state,id,id,solve_state,id,id,id,finish_state from \
		# 	problem.problem_record where happen_time>=%s and happen_time<%s or finish_state='未完成'",(s1,s2))

		cur.execute("select id,main_model,descript,stop_produce,problem_type2,id,id,plan_state,solve_state,finish_state,id,problem_type,id,id,id,\
			duty_person,duty_person2,person,id,happen_time,finish_time,commit_time,flow_num,project_id,model,batch_num,project_count,\
			id,id,back_flag,back_descript,mark from \
			problem.problem_record where happen_time>=%s and happen_time<%s or finish_state='未完成'",(s1,s2))
		li=cur.fetchall()
		conn.commit()
		self.table.setRowCount(len(li))
		rowcount=0
		for i in li:
			columncount=0
			for j in i:
				self.table.setItem(rowcount,columncount,QTableWidgetItem(str(j)))
				columncount+=1
			rowcount+=1
		self.__flush_add__()
		for i in range(self.table.rowCount()):
			if self.table.item(i,29).text()=='退回':
				for j in range(32):
					self.table.item(i,j).setBackground(QBrush(QColor(255,100,100)))

		self.create_df()
		self.create_dic()

	def __flush_add__(self):
		for x in range(self.table.rowCount()):
			problem_id=self.table.item(x,0).text()

			'''
			方案给出人
			'''
			cur.execute("select confirm_person from problem.solve_person where plan_id in (select id \
				from problem.solve_plan where problem_id=%s and plan_state='最新记录')",(problem_id))
			li=cur.fetchall()
			conn.commit()
			if len(li)==0:
				solve_person=''
			if len(li)==1:
				solve_person=li[0][0]
			if len(li)>1:
				solve_person=''
				for i in li:
					solve_person+=i[0]
					solve_person+='/'
								#!!!!
			self.table.setItem(x,14,QTableWidgetItem(str(solve_person)))

			'''
			分析人
			'''
			cur.execute("select confirm_person from problem.analysis_person where analysis_id in (select id \
				from problem.analysis where problem_id=%s and result_state='最新记录')",(problem_id))
			li=cur.fetchall()
			conn.commit()
			if len(li)==0:
				analysis_person=''
			if len(li)==1:
				analysis_person=li[0][0]
			if len(li)>1:
				analysis_person=''
				for i in li:
					analysis_person+=i[0]
					analysis_person+='/'
								#!!!!
			self.table.setItem(x,12,QTableWidgetItem(analysis_person))

			'''
			责任部门
			'''
			cur.execute("select partment from problem.analysis_duty where analysis_id in (select id \
				from problem.analysis where problem_id=%s and result_state='最新记录')",(problem_id))
			li=cur.fetchall()
			conn.commit()
			if len(li)==0:
				analysis_person=''
			if len(li)==1:
				analysis_person=li[0][0]
			if len(li)>1:
				analysis_person=''
				for i in li:
					analysis_person+=i[0]
					analysis_person+='/'
								#!!!!
			self.table.setItem(x,18,QTableWidgetItem(analysis_person))


			'''
			分析质检确认人
			'''
			cur.execute("select confirm_person from problem.analysis_person_quality where analysis_id in (select id \
				from problem.analysis where problem_id=%s and result_state='最新记录')",(problem_id))
			li=cur.fetchall()
			conn.commit()
			if len(li)==0:
				analysis_person=''
			if len(li)==1:
				analysis_person=li[0][0]
			if len(li)>1:
				analysis_person=''
				for i in li:
					analysis_person+=i[0]
					analysis_person+='/'
								#!!!!
			self.table.setItem(x,13,QTableWidgetItem(analysis_person))


			'''
			工艺是否变更和负责人和解决方案
			'''
			cur.execute("select crafts_state,crafts_person,solve from problem.solve_plan where problem_id=%s \
				and plan_state='最新记录'",(problem_id))
			li=cur.fetchall()
			conn.commit()
			if len(li)==1:
				for i in li:		#!!!!
					self.table.setItem(x,27,QTableWidgetItem(str(i[0])))
					self.table.setItem(x,28,QTableWidgetItem(str(i[1])))
					self.table.setItem(x,6,QTableWidgetItem(str(i[2])))
			if len(li)==0:
				self.table.setItem(x,27,QTableWidgetItem(str('')))
				self.table.setItem(x,28,QTableWidgetItem(str('')))
				self.table.setItem(x,6,QTableWidgetItem(str('')))

			'''
			分析结果
			'''
			cur.execute("select result from problem.analysis where problem_id=%s \
				and result_state='最新记录'",(problem_id))
			li=cur.fetchall()
			conn.commit()
			if len(li)==1:			#!!!!
				self.table.setItem(x,5,QTableWidgetItem(str(li[0][0])))
			if len(li)==0:
				self.table.setItem(x,5,QTableWidgetItem(str('')))

			self.table.setItem(x,10,QTableWidgetItem(str(self.plan_finish_state(self.table.item(x,23).text()))))

	def plan_finish_state(self,pro_id):
		pro_id=str(pro_id)
		s=pro_id+'MD5'+pro_id+'dj'
		m=hashlib.md5(s.encode('ascii')).hexdigest()
		print(m)
		s='http://192.168.30.230/jiekou/OrderInfoGet_ById/?id='+pro_id+'&CheckCode='+m
		try:
			r=requests.get(s,timeout=1)
		except:
			return '未知'
		j=r.json()
		if len(j)==0:
			return '未知'
		li=j[0]	
		finished_time=li['完成时间']
		li_datetime=finished_time.split(' ')

		li_date=li_datetime[0].split('/')
		year=int(li_date[0])
		month=int(li_date[1])
		day=int(li_date[2])
		li_time=li_datetime[1].split(':')
		hour=int(li_time[0])
		mini=int(li_time[1])
		sec=int(li_time[2])
		finished_date=datetime.datetime(year,month,day,hour,mini,sec)
		now=datetime.datetime.now()
		if now>=finished_date:
			return '结束'
		if now<finished_date:
			return '未结束'


	def create_df(self):
		len_row=self.table.rowCount()
		len_column=self.table.columnCount()
		li_data=[]
		for i in range(len_row):
			li_temp=[]
			for j in range(len_column):
				li_temp.append(self.table.item(i,j).text())
			li_data.append(li_temp)
		
		self.df=pd.DataFrame(li_data,columns=self.columns)
		# print(self.df)

	def create_dic(self):
		for i in self.columns:
			dic_temp={}
			li=self.df[i].drop_duplicates().tolist()
			for j in li:
				dic_temp[j]=1
			self.dic[i]=dic_temp

		# print(self.dic)


	def add_event(self):
		self.winaddnew=WinCreateProblem(self)
	def table_double_clicked_event(self,row,column):
		self.winviewdetail=WinViewDetail(int(self.table.item(row,0).text()))
	def flush_view_detail(self,problem_id):
		self.winviewdetail=WinViewDetail(problem_id)
	def add_type(self):
		cur.execute("select name from problem.finish_person")
		name=cur.fetchall()[0][0]
		login_flag,name=WinConfirm(name).get_result()
		if login_flag=='fail':
			return

		self.winaddproblemtype=WinAddProblemType(self.table.currentRow(),self.table.item(self.table.currentRow(),0).text(),self)


'''
退回操作
'''
class WinBack(QWidget):
	def __init__(self,record_id,table):
		super().__init__()
		self.table=table
		self.record_id=record_id
		label_descript=QLabel('退回原因',self)
		self.text_descript=QTextEdit(self)
		btn_commit=QPushButton('确定',self)
		btn_commit.clicked.connect(self.commit_event)
		vlayout=QVBoxLayout(self)
		vlayout.addWidget(label_descript,alignment=Qt.AlignLeft)
		vlayout.addWidget(self.text_descript)
		vlayout.addWidget(btn_commit)
		self.setLayout(vlayout)
		self.show()
	def commit_event(self):
		descript=self.text_descript.toPlainText().replace(' ','')
		cur.execute("update problem.problem_record set back_flag='退回',back_descript=%s where id=%s",\
			(descript,self.record_id))
		conn.commit()
		self.close()
		self.table.item(self.table.currentRow(),29).setText('退回')
		self.table.item(self.table.currentRow(),30).setText(descript)
		for i in range(self.table.columnCount()):
			self.table.item(self.table.currentRow(),i).setBackground(QBrush(QColor(255,100,100)))

class WinMark(QWidget):
	def __init__(self,record_id,table):
		super().__init__()
		self.table=table
		self.record_id=record_id
		label_descript=QLabel('标记内容',self)
		self.text_descript=QLineEdit(self)
		btn_commit=QPushButton('确定',self)
		btn_commit.clicked.connect(self.commit_event)
		vlayout=QVBoxLayout(self)
		vlayout.addWidget(label_descript,alignment=Qt.AlignLeft)
		vlayout.addWidget(self.text_descript)
		vlayout.addWidget(btn_commit)
		self.setLayout(vlayout)
		self.show()
	def commit_event(self):
		descript=self.text_descript.text().replace(' ','')
		cur.execute("update problem.problem_record set mark=%s where id=%s",(descript,self.record_id))
		conn.commit()
		self.close()
		self.table.item(self.table.currentRow(),31).setText(descript)


class WinSelectFilter(QWidget):

	def __init__(self,df,columns,column,dic,table):
		super().__init__()
		self.df=df
		self.columns=columns
		self.column=column
		self.dic=dic
		self.table=table
		self.li_checkbox=[]

		layout=QVBoxLayout()

		self.check_all=QCheckBox('全选',self)
		self.check_all.setCheckState(2)
		self.check_all.setTristate(False)
		self.check_all.stateChanged.connect(self.statechanged_all)
		self.check_all.clicked.connect(self.clicked_all)
		self.btn_commit=QPushButton('确定',self)
		self.btn_commit.clicked.connect(self.commit_event)
		layout.addWidget(self.check_all)

		li_item=self.filter_data_temp()[self.columns[self.column]].drop_duplicates().tolist()
		len_off=0
		len_on=0
		len_li=len(li_item)
		for i in li_item:
			c=QCheckBox(str(i),self)
			if self.dic[self.columns[self.column]][i]==1:
				c.setCheckState(2)
				len_on+=1
			if self.dic[self.columns[self.column]][i]==0:
				c.setCheckState(0)
				len_off+=1
			self.li_checkbox.append(c)
			c.stateChanged.connect(self.statechanged)
			layout.addWidget(c)

		if len_off==len_li:
			self.check_all.setCheckState(0)
		if len_on==len_li:
			self.check_all.setCheckState(2)
		if len_on<len_li and len_off<len_li:
			self.check_all.setCheckState(1)



		
		widget=QWidget(self)
		widget.setLayout(layout)
		# widget.setMinimumHeight(600)
		scroll=QScrollArea(self)
		scroll.setWidget(widget)
		# scroll.setMaximumHeight(600)
		layout_scroll=QVBoxLayout()
		layout_scroll.addWidget(scroll)
		layout_scroll.addWidget(self.btn_commit,alignment=Qt.AlignCenter)
		self.setLayout(layout_scroll)
		self.show()

	def clicked_all(self):
		sender = self.sender()
		if sender.checkState()==1:
			sender.setCheckState(2)

	def statechanged_all(self,state):
		print(self.check_all.isTristate())
		if state==2:
			self.btn_commit.setEnabled(True)
			for i in self.li_checkbox:
				i.setCheckState(2)
		if state==0:
			self.btn_commit.setEnabled(False)
			for i in self.li_checkbox:
				i.setCheckState(0)
		if state==1:
			self.btn_commit.setEnabled(True)

	def statechanged(self,state):
		sender = self.sender()
		print(sender.text())
		# if sender.checkState==2:
		# 	self.dic[self.columns[column]][sender.text()]=1
		# if sender.checkState==0:
		# 	self.dic[self.columns[column]][sender.text()]=0
		len_li=len(self.li_checkbox)
		len_off=0
		len_on=0
		for i in self.li_checkbox:
			if i.checkState()==2:
				len_on+=1
			if i.checkState()==0:
				len_off+=1
		if len_off==len_li:
			self.check_all.setCheckState(0)
		if len_on==len_li:
			self.check_all.setCheckState(2)
		if len_on<len_li and len_off<len_li:
			self.check_all.setCheckState(1)
		print('KKKKKKKKKKKKK')
		print(len_li)
		print(len_off)
		print(len_on)

		

	def commit_event(self):
		if self.check_all.checkState()==2:
			for i in self.dic[self.columns[self.column]].keys():
				self.dic[self.columns[self.column]][i]=1
		if self.check_all.checkState()==1:
			for i in self.li_checkbox:
				if i.checkState()==2:
					self.dic[self.columns[self.column]][i.text()]=1
				if i.checkState()==0:
					self.dic[self.columns[self.column]][i.text()]=0
			print('diccccccccc',self.dic[self.columns[self.column]])
		self.filter_data()
		self.close()



	def filter_data_temp(self):
		li=self.columns.copy()
		li.pop(self.column)
		df=self.filter_base(li)
		return df

	def filter_data(self):
		df=self.filter_base(self.columns.copy())
		li=df.values
		self.table.setRowCount(0)
		self.table.setRowCount(len(li))
		rowcount=0
		for i in li:
			columncount=0
			for j in i:
				self.table.setItem(rowcount,columncount,QTableWidgetItem(str(j)))
				columncount+=1
			rowcount+=1

	def filter_base(self,li_column):
		print(li_column)
		df_judge=self.df['id']!='S'
		for i in li_column:
			li_temp=[]
			print('iiiiiiiii',i)
			dic_temp=self.dic[i]
			for j in dic_temp.keys():
				if dic_temp[j]==1:
					li_temp.append(j)
			df_judge=self.df[i].isin(li_temp)&df_judge
		df=self.df[df_judge]
		return df


		
class WinAddProblemType(QWidget):
	def __init__(self,rowcount,problem_id,parent):
		super().__init__()
		self.problem_id=problem_id
		self.parent=parent
		self.rowcount=rowcount
		self.initUI()
		
	def initUI(self):
		btn_commit=QPushButton('确定',self)
		btn_commit.clicked.connect(self.commit_event)
		self.lineedit_type=QLineEdit(self)

		vlayout=QVBoxLayout(self)
		vlayout.addWidget(self.lineedit_type)
		vlayout.addWidget(btn_commit,alignment=Qt.AlignCenter)

		self.setLayout(vlayout)
		self.setWindowTitle('问题分类')
		self.show()

	def commit_event(self):
		pro_type=self.lineedit_type.text()
		cur.execute("update problem.problem_record set problem_type=%s where id=%s",(pro_type,self.problem_id))
		conn.commit()
		self.close()
		self.parent.table.item(self.rowcount,11).setText(str(pro_type))



'''
增加影响结束日期界面
'''
class WinAddFinishDate(QWidget):
	def __init__(self,rowcount,problem_id,parent):
		super().__init__()
		self.problem_id=problem_id
		self.parent=parent
		self.rowcount=rowcount
		self.initUI()
		

	def initUI(self):

		label_date=QLabel('结束日期',self)
		self.line_date=QDateTimeEdit(QDateTime.currentDateTime(),self)
		btn_commit=QPushButton('确定',self)
		btn_commit.clicked.connect(self.commit_event)
		glayout=QGridLayout(self)
		glayout.addWidget(label_date,0,0)
		glayout.addWidget(self.line_date,0,1)
		glayout.addWidget(btn_commit,1,0,1,2,alignment=Qt.AlignCenter)

		self.setLayout(glayout)
		self.show()

	def commit_event(self):
		finish_time=self.line_date.dateTime().toString('yyyy-MM-dd hh:mm')
		cur.execute("update problem.problem_record set finish_time=%s where id=%s",(finish_time,self.problem_id))
		conn.commit()

		self.close()

		self.parent.table.item(self.rowcount,20).setText(str(finish_time))

'''
显示修改负责人界面
'''
class WinModifyDutyPerson(QDialog):
	def __init__(self,defult_name=''):
		super().__init__()
		self.defult_name=defult_name
		self.initUI()
		


	def initUI(self):
		self.name=''
		self.login_flag='fail'
		label_modify=QLabel('修改为',self)
		self.lineedit_old_name=QLineEdit(self)
		self.lineedit_old_name.setReadOnly(True)
		self.lineedit_old_name.setText(self.defult_name)
		self.lineedit_new_name=QLineEdit(self)
		btn_commit=QPushButton('确定',self)
		btn_commit.clicked.connect(self.commit_event)

		glayout=QGridLayout(self)
		glayout.addWidget(self.lineedit_old_name,0,0)
		glayout.addWidget(label_modify,0,1)
		glayout.addWidget(self.lineedit_new_name,0,2)
		glayout.addWidget(btn_commit,1,1)

		self.setLayout(glayout)
		self.show()
		self.exec()

	def commit_event(self):
		self.name=self.lineedit_new_name.text()
		self.login_flag='success'
		print('success')
		time.sleep(1)
		self.close()

	def get_result(self):

		return self.login_flag,self.name


'''
显示问题跟踪记录
'''
class WinTrackRecord(QGroupBox):
	def __init__(self,problem_id):
		super().__init__('跟踪记录')
		self.problem_id=problem_id
		self.initUI()

	def initUI(self):
		self.table=QTableWidget(0,4,self)
		self.table.setHorizontalHeaderLabels(['ID','描述','姓名','时间'])
		self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
		btn_add=QPushButton('添加',self)
		btn_add.clicked.connect(self.add_event)
		vlayout=QVBoxLayout(self)
		vlayout.addWidget(self.table)
		vlayout.addWidget(btn_add,alignment=Qt.AlignRight)
		self.setLayout(vlayout)
		self.show()
		self.load_data()
		self.setMinimumWidth(500)

	def load_data(self):
		cur.execute("select id,descript,confirm_person,confirm_time from problem.track_record where problem_id=%s",(self.problem_id))
		li=cur.fetchall()
		conn.commit()
		self.table.setRowCount(len(li))
		rowcount=0
		for i in li:
			columncount=0
			for j in i:
				self.table.setItem(rowcount,columncount,QTableWidgetItem(str(j)))
				columncount+=1
			rowcount+=1


	def add_event(self):
		self.winaddtrackrecord=WinAddTrackRecord(self.problem_id,self.table)


'''
显示添加问题跟踪记录
'''
class WinAddTrackRecord(QWidget):
	def __init__(self,problem_id,table):
		super().__init__()
		self.problem_id=problem_id
		self.table=table
		self.initUI()

	def initUI(self):
		label_descript=QLabel('描述',self)
		self.textedit_descript=QTextEdit(self)
		btn_commit=QPushButton('确定',self)
		btn_commit.clicked.connect(self.commit_event)
		vlayout=QVBoxLayout(self)
		vlayout.addWidget(label_descript,alignment=Qt.AlignLeft)
		vlayout.addWidget(self.textedit_descript)
		vlayout.addWidget(btn_commit,alignment=Qt.AlignRight)
		self.setLayout(vlayout)
		self.show()
	def commit_event(self):
		descript=self.textedit_descript.toPlainText()
		login_flag,name=WinConfirm().get_result()
		if login_flag=='fail':
			return
		now=datetime.datetime.now()
		now=str(now)[0:19]
		cur.execute("insert into problem.track_record (problem_id,descript,confirm_person,confirm_time) \
			values (%s,%s,%s,%s)",(self.problem_id,descript,name,now))

		cur.execute("select id,descript,confirm_person,confirm_time from problem.track_record where \
			id=(select max(id) from problem.track_record)")

		li=cur.fetchall()
		conn.commit()
		self.table.setRowCount(self.table.rowCount()+1)
		columncount=0
		for i in li[0]:
			self.table.setItem(self.table.rowCount()-1,columncount,QTableWidgetItem(str(i)))
			columncount+=1
		self.close()


class PrintExcel():
	def __init__(self,main_id,parent):
		self.main_id=main_id
		self.parent=parent

	def init(self):
		try:
			self.exapp = win32com.client.Dispatch("Excel.Application")
		except:
			QMessageBox(text='   无法打开excel程序！  ',parent=self.parent).show()
			print('无法打开excel程序 异常')
			return
		self.exapp.Visible = False
		if not os.path.exists("./template.xlsx"):
			QMessageBox(text='   模板文件不存在！  ',parent=self.parent).show()
			return
		print(os.getcwd())
		filepath=os.getcwd()
		self.work_book = self.exapp.Workbooks.Open(filepath+"/template.xlsx")
		self.sheet=self.work_book.Worksheets('Sheet1')

	def write(self):
		cur.execute("select flow_num,project_id,model,batch_num,project_count,person,happen_time,descript \
			from problem.problem_record where id=%s",(self.main_id))
		li=cur.fetchall()[0]
		li_loc=[['2','K'],['4','B'],['4','F'],['4','I'],['4','L'],['5','B'],['5','F'],['7','A']]
		for i in range(len(li)):
			self.write_date(li_loc[i][0],li_loc[i][1],str(li[i]))

		cur.execute("select solve,confirm_time from problem.solve_plan where problem_id=%s and \
			plan_state='最新记录'",(self.main_id))
		li=cur.fetchall()
		if len(li)==1:
			li=li[0]
			self.write_date(9,'A',li[0])

			s='方案确认时间：'+str(li[1])
			self.write_date(21,'H',s)

			cur.execute("select confirm_person from problem.solve_person where plan_id in (select id from \
				problem.solve_plan where problem_id=%s and plan_state='最新记录')",(self.main_id))
			li=cur.fetchall()
			s='方案给出人：'
			for i in li:
				s+=str(i[0])
				s+='/'
			self.write_date(21,'A',s)
			cur.execute("select material_state,way_state from problem.solve_plan where problem_id=%s and \
				plan_state='最新记录'",(self.main_id))
			li=cur.fetchall()[0]
			material_state=li[0]
			way_state=li[1]
			li_column=['A','C','E','G','J','K','L']
			li_loc=[]
			if material_state=='有':
				for i in range(12,17):
					li_temp=[]
					for j in li_column:
						li_temp.append([str(i),j])
					li_loc.append(li_temp)

				cur.execute("select operate_type,material_num,material_name,material_model,material_count,\
					partment,confirm_person from problem.solve_material where plan_id in (select id from \
						problem.solve_plan where problem_id=%s and plan_state='最新记录')",(self.main_id))
				li=cur.fetchall()
				lenth=len(li)
				if lenth>5:
					lenth=5

				for i in range(lenth):
					for j in range(len(li[0])):
						self.write_date(li_loc[i][j][0],li_loc[i][j][1],str(li[i][j]))
			if way_state=='区分':
				cur.execute("select split_way from problem.solve_plan  where problem_id=%s and \
					plan_state='最新记录'",(self.main_id))
				li=cur.fetchall()[0]
				self.write_date(18,'A','区分')
				self.write_date(19,'A',str(li[0]))
			else:
				self.write_date(18,'A','不区分')

		cur.execute("select result,commit_time from problem.analysis where problem_id=%s and \
			result_state='最新记录'",(self.main_id))
		li=cur.fetchall()
		if len(li)==1:
			self.write_date(23,'A',li[0][0])

			s='分析确认时间：'+str(li[0][1])
			self.write_date(27,'H',s)

			cur.execute("select confirm_person from problem.analysis_person where analysis_id in (select id from \
				problem.analysis where problem_id=%s and result_state='最新记录')",(self.main_id))
			li=cur.fetchall()
			s='分析人：'
			for i in li:
				s+=str(i[0])
				s+='/'
			self.write_date(27,'A',s)

			cur.execute("select confirm_person from problem.analysis_person_quality where analysis_id in (select id from \
				problem.analysis where problem_id=%s and result_state='最新记录')",(self.main_id))
			li=cur.fetchall()
			if len(li)!=0:
				s='质检确认人：'
				for i in li:
					s+=str(i[0])
					s+='/'
				self.write_date(28,'A',s)

			cur.execute("select max(confirm_time) from problem.analysis_person_quality where analysis_id in (select id from \
				problem.analysis where problem_id=%s and result_state='最新记录')",(self.main_id))
			li=cur.fetchall()
			if li[0][0] is not None:
				s='质检确认时间：'+str(li[0][0])
				self.write_date(28,'H',s)

			li_loc=[]
			for i in range(25,27):
				for j in ['A','C','E','G','I','K']:
					li_loc.append([str(i),j])
			cur.execute("select partment from problem.analysis_duty where analysis_id in (select id from \
				problem.analysis where problem_id=%s and result_state='最新记录')",(self.main_id))

			li=cur.fetchall()
			for i in range(len(li)):
				self.write_date(li_loc[i][0],li_loc[i][1],li[i][0])

			li_loc=[]
			li_column=['C','E','G','H','I','J','K','L']
			for i in li_column:
				li_temp=[]
				for j in range(30,36):
					li_temp.append([str(j),i])
				li_loc.append(li_temp)

			cur.execute("select line_name,effect_date,workhour_manage,workhour_technology,\
				workhour_operate,confirm_person from problem.work_hour where problem_id=%s",(self.main_id))
			li=cur.fetchall()
			for i in range(len(li)):
				for j in range(len(li[i])):
					self.write_date(li_loc[i][j][0],li_loc[i][j][1],str(li[i][j]))

		


	def write_date(self,row,column,content):
		self.sheet.Cells(str(row),str(column)).Value=str(content)

	def workbook_save(self):
		self.init()
		self.write()
		d=str(datetime.datetime.now())[0:19]
		s='D:/问题记录'+d[0:4]+d[5:7]+d[8:10]+d[11:13]+d[14:16]+d[17:19]
		filename=QFileDialog.getSaveFileName(QWidget(),'存储为',s,'xlsx')
		if filename[0]=='':
			return
		filename=filename[0]+'.'+filename[1]
		filename=filename.replace('/','\\')
		self.work_book.SaveAs(filename)
		self.workbook_close()

	def workbook_close(self):

		d=str(datetime.datetime.now())[0:19]
		s=d[0:4]+d[5:7]+d[8:10]+d[11:13]+d[14:16]+d[17:19]
		s='C:\\problemrecord\\'+s+'.xlsx'
		if not os.path.exists('C:/problemrecord'):
			os.mkdir('C:/problemrecord')
		self.work_book.Close(SaveChanges=True,Filename=s)
		self.exapp.Quit()

	def print_date(self):
		self.init()
		self.write()
		try:
			self.sheet.PrintOut()
		except:
			QMessageBox(text='   打印失败！  ',parent=self.parent).show()
			return
		self.workbook_close()




'''
显示详细细节,问题，分析，解决方案
'''
class WinViewDetail(QScrollArea):
	def __init__(self,main_id):
		super().__init__()
		self.main_id=main_id
		self.initUI()

	def initUI(self):
		btn_print=QPushButton('打印',self)
		btn_print.clicked.connect(self.print_event)
		btn_out=QPushButton('输出excel文件',self)
		btn_out.clicked.connect(self.print_out)
		vlayout_a=QVBoxLayout()
		vlayout_b=QVBoxLayout()
		vlayout_c=QVBoxLayout()
		hlayout=QHBoxLayout()	
		vlayout_a.addWidget(WinViewProblem(self.main_id),alignment=Qt.AlignTop)
		vlayout_c.addWidget(WinViewWorkHour(self.main_id),alignment=Qt.AlignTop)
		vlayout_a.addWidget(WinViewPlan(self.main_id),alignment=Qt.AlignTop)
		vlayout_a.addStretch(1)
		vlayout_b.addWidget(WinViewSolve(self.main_id),alignment=Qt.AlignTop)
		vlayout_b.addStretch(1)
		vlayout_c.addWidget(WinTrackRecord(self.main_id),alignment=Qt.AlignTop)
		vlayout_c.addStretch(1)
		hlayout.addLayout(vlayout_a)
		hlayout.addLayout(vlayout_b)
		hlayout.addLayout(vlayout_c)
		vlayout_all=QVBoxLayout(self)
		hlayout_t=QHBoxLayout()
		hlayout_t.addWidget(btn_out,alignment=Qt.AlignRight)
		hlayout_t.addWidget(btn_print,alignment=Qt.AlignRight)
		vlayout_all.addLayout(hlayout_t)
		vlayout_all.addLayout(hlayout)

		self.widget=QWidget()
		self.widget.setLayout(vlayout_all)
		self.setWidget(self.widget)
		self.show()
		self.setWindowTitle('详细记录')
		self.setWindowState(Qt.WindowMaximized)

		# glayout=QGridLayout(self)		
		# glayout.addWidget(WinViewProblem(self.main_id),0,0,alignment=Qt.AlignTop)
		# glayout.addWidget(WinViewWorkHour(self.main_id),1,2,alignment=Qt.AlignTop)
		# glayout.addWidget(WinViewPlan(self.main_id),1,0,alignment=Qt.AlignTop)
		# glayout.addWidget(WinViewSolve(self.main_id),0,1,2,1,alignment=Qt.AlignTop)
		# glayout.addWidget(WinTrackRecord(self.main_id),0,2,2,1,alignment=Qt.AlignTop)
		# self.widget=QWidget()
		# self.widget.setLayout(glayout)
		# self.setWidget(self.widget)
		# self.show()
	def print_out(self):
		ex=PrintExcel(self.main_id,self)
		ex.workbook_save()


	def print_event(self):
		ex=PrintExcel(self.main_id,self)
		ex.print_date()



'''
显示异常问题
'''
class WinViewProblem(QGroupBox):
	def __init__(self,main_id):
		super().__init__('问题详情')
		self.main_id=main_id
		self.initUI()

	def initUI(self):
		label_plan_id=QLabel('计划ID',self)
		label_model_main=QLabel('主型号',self)
		label_model=QLabel('系列号',self)
		label_batch=QLabel('批次',self)
		label_plan_count=QLabel('计划数量',self)
		label_happen_time=QLabel('发生时间',self)
		label_person=QLabel('提交人',self)
		label_commit_time=QLabel('提交时间',self)
		label_descript=QLabel('异常情况说明',self)
		label_stop_produce=QLabel('生产影响',self)
		label_problem_type=QLabel('问题分类',self)


		self.lineedit_plan_id=QLineEdit(self)	
		self.lineedit_model_main=QLineEdit(self)
		self.lineedit_model=QLineEdit(self)
		self.lineedit_batch=QLineEdit(self)
		self.lineedit_count=QLineEdit(self)
		self.lineedit_happen_time=QLineEdit(self)
		self.lineedit_person=QLineEdit(self)
		self.lineedit_commit_time=QLineEdit(self)
		self.textedit_descript=QTextEdit(self)
		self.lineedit_stop_produce=QLineEdit(self)
		self.lineedit_problem_type=QLineEdit(self)

		self.lineedit_plan_id.setReadOnly(True)
		self.lineedit_model_main.setReadOnly(True)
		self.lineedit_model.setReadOnly(True)
		self.lineedit_batch.setReadOnly(True)
		self.lineedit_count.setReadOnly(True)
		self.lineedit_happen_time.setReadOnly(True)
		self.lineedit_person.setReadOnly(True)
		self.lineedit_commit_time.setReadOnly(True)
		self.textedit_descript.setReadOnly(True)
		self.lineedit_stop_produce.setReadOnly(True)
		self.lineedit_problem_type.setReadOnly(True)

		glayout=QGridLayout(self)
		glayout.addWidget(label_plan_id,0,0)
		glayout.addWidget(self.lineedit_plan_id,0,1)
		glayout.addWidget(label_plan_count,0,2)
		glayout.addWidget(self.lineedit_count,0,3)	

		glayout.addWidget(label_model_main,1,0)
		glayout.addWidget(self.lineedit_model_main,1,1)
		glayout.addWidget(label_model,1,2)
		glayout.addWidget(self.lineedit_model,1,3)

		glayout.addWidget(label_batch,2,0)
		glayout.addWidget(self.lineedit_batch,2,1)
		glayout.addWidget(label_happen_time,2,2)
		glayout.addWidget(self.lineedit_happen_time,2,3)

		glayout.addWidget(label_stop_produce,3,0)
		glayout.addWidget(self.lineedit_stop_produce,3,1)
		glayout.addWidget(label_problem_type,3,2)
		glayout.addWidget(self.lineedit_problem_type,3,3)

		glayout.addWidget(label_person,3+1,0)
		glayout.addWidget(self.lineedit_person,3+1,1)
		glayout.addWidget(label_commit_time,3+1,2)
		glayout.addWidget(self.lineedit_commit_time,3+1,3)
	
		glayout.addWidget(label_descript,4+1,0,1,4)
		glayout.addWidget(self.textedit_descript,5+1,0,1,4)

		self.setLayout(glayout)
		self.get_date()

		self.show()

	def get_date(self):
		cur.execute("select project_id,project_count,main_model,model,\
			batch_num,happen_time,person,commit_time,descript,stop_produce,problem_type2 from problem.problem_record where id=%s",(self.main_id))
		li=cur.fetchall()[0]
		conn.commit()

		self.lineedit_plan_id.setText(str(li[0]))
		self.lineedit_count.setText(str(li[1]))
		self.lineedit_model_main.setText(str(li[2]))
		self.lineedit_model.setText(str(li[3]))
		self.lineedit_batch.setText(str(li[4]))
		self.lineedit_happen_time.setText(str(li[5]))
		self.lineedit_person.setText(str(li[6]))
		self.lineedit_commit_time.setText(str(li[7]))
		self.textedit_descript.setPlainText(str(li[8]))
		self.lineedit_stop_produce.setText(str(li[9]))
		self.lineedit_problem_type.setText(str(li[10]))

'''
显示全部的分析
'''
class WinViewPlan(QGroupBox):
	def __init__(self,main_id):
		super().__init__('分析结果')
		self.main_id=main_id
		self.initUI()

	def initUI(self):
		vlayout=QVBoxLayout(self)
		cur.execute("select id from problem.analysis where problem_id=%s",(str(self.main_id)))
		li=cur.fetchall()
		conn.commit()
		for i in li:
			vlayout.addWidget(WinViewPlanOnce(i[0],self.main_id,self))
		if len(li)==0:
			vlayout.addWidget(WinViewPlanOnce(0,self.main_id,self))
		self.setLayout(vlayout)
		self.show()



'''
显示一次的分析
'''
class WinViewPlanOnce(QWidget):
	def __init__(self,analysis_id,problem_id,parent):
		super().__init__()
		self.analysis_id=analysis_id
		self.problem_id=problem_id
		self.parent=parent
		self.initUI()

	def initUI(self):
		btn_modify=QPushButton('修改',self)
		btn_add=QPushButton('添加',self)
		btn_add_name_quality=QPushButton('添加',self)

		btn_modify.clicked.connect(self.modify_event)
		btn_add.clicked.connect(self.add_event)
		btn_add_name_quality.clicked.connect(self.add_name_quality)

		label_confirm_person=QLabel('分析确认人',self)
		label_confirm_person_quality=QLabel('质检确认人',self)
		label_commit_time=QLabel('提交时间',self)
		label_state=QLabel('状态',self)
		label_duty_partment=QLabel('责任部门',self)
		label_result=QLabel('分析结果',self)

		self.lineedit_confirm_person=QLineEdit(self)
		self.lineedit_confirm_person_quality=QLineEdit(self)
		self.lineedit_commit_time=QLineEdit(self)
		self.lineedit_state=QLineEdit(self)
		self.lineedit_duty_partment=QLineEdit(self)
		self.textedit_result=QTextEdit(self)

		self.lineedit_confirm_person.setReadOnly(True)
		self.lineedit_confirm_person_quality.setReadOnly(True)
		self.lineedit_commit_time.setReadOnly(True)
		self.lineedit_state.setReadOnly(True)
		self.lineedit_duty_partment.setReadOnly(True)
		self.textedit_result.setReadOnly(True)

		glayout=QGridLayout(self)
		glayout.addWidget(label_confirm_person,0,0)
		glayout.addWidget(self.lineedit_confirm_person,0,1,1,3)
		glayout.addWidget(label_confirm_person_quality,1,0)
		glayout.addWidget(self.lineedit_confirm_person_quality,1,1,1,2)
		glayout.addWidget(btn_add_name_quality,1,3,alignment=Qt.AlignRight)
		glayout.addWidget(label_commit_time,1+1,0)
		glayout.addWidget(self.lineedit_commit_time,1+1,1)
		glayout.addWidget(label_state,1+1,2)
		glayout.addWidget(self.lineedit_state,1+1,3)
		glayout.addWidget(label_duty_partment,2+1,0)
		glayout.addWidget(self.lineedit_duty_partment,2+1,1,1,3)
		glayout.addWidget(label_result,3+1,0)
		glayout.addWidget(self.textedit_result,4+1,0,1,4)
		glayout.addWidget(btn_modify,5+1,2)
		glayout.addWidget(btn_add,5+1,3,alignment=Qt.AlignRight)

		self.setLayout(glayout)
		self.show()

		cur.execute("select plan_state,finish_state from problem.problem_record where id=%s",(str(self.problem_id)))
		li=cur.fetchall()[0]
		conn.commit()
		print('>>>>>>>>>>>>>>>>>>>>',li)
		if li[1]=='未完成':
			if li[0]=='已完成':
				btn_modify.setEnabled(False)
				btn_add.setEnabled(False)

			# btn_add_name_quality.setEnabled(False)
		if li[1]=='已完成':
			btn_modify.setEnabled(False)
			btn_add.setEnabled(False)

		if self.analysis_id==0:
			btn_modify.setEnabled(False)
			btn_add_name_quality.setEnabled(False)
			return


		cur.execute("select result,commit_time,result_state from problem.analysis where id=%s",(self.analysis_id))
		li=cur.fetchall()[0]
		conn.commit()
		if li[2]=='历史记录':
			btn_modify.setEnabled(False)
			btn_add.setEnabled(False)
			btn_add_name_quality.setEnabled(False)
		
		self.textedit_result.setPlainText(str(li[0]))
		self.lineedit_commit_time.setText(str(li[1]))
		self.lineedit_state.setText(str(li[2]))

		btn_add.setEnabled(False)

		
		cur.execute("select confirm_person from problem.analysis_person where analysis_id=%s",(self.analysis_id))
		li=cur.fetchall()
		conn.commit()
		names=''
		for i in li:
			names+='/'
			names+=i[0]
		self.lineedit_confirm_person.setText(names)

		cur.execute("select confirm_person from problem.analysis_person_quality where analysis_id=%s",(self.analysis_id))
		li=cur.fetchall()
		conn.commit()
		names=''
		for i in li:
			names+='/'
			names+=i[0]
		self.lineedit_confirm_person_quality.setText(names)

		cur.execute("select partment from problem.analysis_duty where analysis_id=%s",(self.analysis_id))
		li=cur.fetchall()
		conn.commit()
		dutys=''
		for i in li:
			dutys+='/'
			dutys+=i[0]
		self.lineedit_duty_partment.setText(dutys)

	def add_name_quality(self):
		winconfirm=WinConfirm()
		login_flag,name=winconfirm.get_result()
		if login_flag=='success':
			now=datetime.datetime.now()
			now=str(now)[0:19]
			cur.execute("insert into problem.analysis_person_quality (analysis_id,confirm_person,confirm_time) \
				values (%s,%s,%s)",(self.analysis_id,str(name),now))
			self.lineedit_confirm_person_quality.setText(self.lineedit_confirm_person_quality.text()+'/'+name)

	def add_event(self):
		print('添加事件')
		self.winaddplan=WinAddPlan(self.problem_id,self)

	def modify_event(self):
		self.winmodifyplan=WinModifyPlan(self.analysis_id,self.problem_id,self)


'''
修改分析结果
'''
class WinModifyPlan(QWidget):
	def __init__(self,analysis_id,problem_id,parent):
		super().__init__()
		self.analysis_id=analysis_id
		self.problem_id=problem_id
		self.parent=parent
		self.li_name=[]
		self.li_name_quality=[]
		self.li_checkbox=[]
		self.initUI()

	def initUI(self):
		btn_commit=QPushButton('提交',self)
		btn_commit.clicked.connect(self.commit_event)
		label_person=QLabel('分析确认人',self)
		label_person_quality=QLabel('质检确认人',self)
		label_result=QLabel('分析结果',self)
		label_duty_partment=QLabel('责任归类',self)

		self.lineedit_person=QLineEdit(self)
		self.lineedit_person.setReadOnly(True)
		self.lineedit_person_quality=QLineEdit(self)
		self.lineedit_person_quality.setReadOnly(True)
		self.textedit_result=QTextEdit(self)
		self.check_yf=QCheckBox('研发部',self)
		self.check_zc=QCheckBox('资材部',self)
		self.check_pz=QCheckBox('品质部',self)
		self.check_jg=QCheckBox('加工厂',self)
		self.check_zz=QCheckBox('产品制造科',self)
		self.check_js=QCheckBox('生产技术科',self)
		self.check_yy=QCheckBox('计划运营科',self)
		self.check_finaly=QCheckBox('最终确认(勾选后将无法对该分析进行修改)')
		self.check_finaly.setCheckState(0)
		
		self.li_checkbox.append(self.check_yf)
		self.li_checkbox.append(self.check_zc)
		self.li_checkbox.append(self.check_pz)
		self.li_checkbox.append(self.check_jg)
		self.li_checkbox.append(self.check_zz)
		self.li_checkbox.append(self.check_js)
		self.li_checkbox.append(self.check_yy)

		glayout=QGridLayout(self)

		glayout.addWidget(label_person,0,0)
		glayout.addWidget(self.lineedit_person,0,1,1,3)
		glayout.addWidget(label_person_quality,1,0)
		glayout.addWidget(self.lineedit_person_quality,1,1,1,3)
		glayout.addWidget(label_duty_partment,1+1,0)
		glayout.addWidget(self.check_yf,1+1,1)
		glayout.addWidget(self.check_zc,1+1,2)
		glayout.addWidget(self.check_pz,1+1,3)
		glayout.addWidget(self.check_jg,2+1,0)
		glayout.addWidget(self.check_zz,2+1,1)
		glayout.addWidget(self.check_js,2+1,2)
		glayout.addWidget(self.check_yy,2+1,3)
		glayout.addWidget(label_result,3+1,0)
		glayout.addWidget(self.textedit_result,4+1,0,1,4)
		glayout.addWidget(self.check_finaly,5+1,0,1,3)
		glayout.addWidget(btn_commit,5+1,3)


		self.setLayout(glayout)
		self.show()
		self.flush_data()

	def flush_data(self):
		cur.execute("select confirm_person from problem.analysis_person where analysis_id=%s",(self.analysis_id))
		li=cur.fetchall()
		conn.commit()
		names=''
		for i in li:
			self.li_name.append(i[0])
			names+='/'
			names+=i[0]
		self.lineedit_person.setText(names)

		cur.execute("select confirm_person from problem.analysis_person_quality where analysis_id=%s",(self.analysis_id))
		li=cur.fetchall()
		conn.commit()
		names=''
		for i in li:
			self.li_name_quality.append(i[0])
			names+='/'
			names+=i[0]
		self.lineedit_person_quality.setText(names)

		cur.execute("select partment from problem.analysis_duty where analysis_id=%s",(self.analysis_id))
		li=cur.fetchall()
		conn.commit()
		dutys=''
		li_checkbox_temp=[]
		for i in li:
			li_checkbox_temp.append(i[0])

		for i in li_checkbox_temp:
			for j in self.li_checkbox:
				if i==j.text():
					j.setCheckState(2)

		cur.execute("select result from problem.analysis where id=%s",(self.analysis_id))
		li=cur.fetchall()
		conn.commit()
		self.textedit_result.setPlainText(str(li[0][0]))

	def commit_event(self):
		if len(self.li_name)==0:
			QMessageBox(text='   请添加确认人！  ',parent=self).show()
			return

		for i in self.li_name:
			winconfirm=WinConfirm(i)
			login_flag,name=winconfirm.get_result()
			if login_flag=='fail':
				QMessageBox(text='   操作已放弃！  ',parent=self).show()
				return
		for i in self.li_name_quality:
			winconfirm=WinConfirm(i)
			login_flag,name=winconfirm.get_result()
			if login_flag=='fail':
				QMessageBox(text='   操作已放弃！  ',parent=self).show()
				return
		if self.check_finaly.checkState()==0:
			problem_plan_state='已分析'
		if self.check_finaly.checkState()==2:
			problem_plan_state='已完成'
		result=self.textedit_result.toPlainText()
		now=datetime.datetime.now()
		now=str(now)[0:19]
		cur.execute("update problem.problem_record set plan_state=%s where id=%s",(problem_plan_state,str(self.problem_id)))
		cur.execute("update problem.analysis set result_state='历史记录' where problem_id=%s",(self.problem_id))
		cur.execute("insert into problem.analysis (problem_id,result,result_state,commit_time) \
			values (%s,%s,%s,%s)",(str(self.problem_id),result,'最新记录',now))
		cur.execute("select max(id) from problem.analysis")
		analysis_id=cur.fetchall()[0][0]
		analysis_id=str(analysis_id)
		for i in self.li_name:
			cur.execute("insert into problem.analysis_person (analysis_id,confirm_person) \
				values (%s,%s)",(analysis_id,str(i)))
		for i in self.li_name_quality:
			cur.execute("insert into problem.analysis_person_quality (analysis_id,confirm_person,confirm_time) \
				values (%s,%s,%s)",(analysis_id,str(i),now))
		for i in self.li_checkbox:
			if i.checkState()==2:
				cur.execute("insert into problem.analysis_duty (analysis_id,partment) \
					values (%s,%s)",(analysis_id,str(i.text())))
		conn.commit()
		self.close()
		winmain.winnofinish.flush_view_detail(self.problem_id)



'''
添加分析结果
'''
class WinAddPlan(QWidget):
	def __init__(self,problem_id,parent):
		super().__init__()
		self.problem_id=problem_id
		self.parent=parent
		self.li_name=[]
		self.li_name_quality=[]
		self.initUI()

	def initUI(self):
		btn_add_name=QPushButton('添加确认人',self)
		btn_add_name.clicked.connect(self.add_name_event)
		btn_add_name_quality=QPushButton('添加确认人',self)
		btn_add_name_quality.clicked.connect(self.add_name_quality)
		btn_commit=QPushButton('提交',self)
		btn_commit.clicked.connect(self.commit_event)
		label_person=QLabel('分析确认人',self)
		label_person_quality=QLabel('质检确认人',self)
		label_result=QLabel('分析结果',self)
		label_duty_partment=QLabel('责任归类',self)
		self.lineedit_person=QLineEdit(self)
		self.lineedit_person.setReadOnly(True)
		self.lineedit_person_quality=QLineEdit(self)
		self.lineedit_person_quality.setReadOnly(True)
		self.textedit_result=QTextEdit(self)
		self.check_yf=QCheckBox('研发部',self)
		self.check_zc=QCheckBox('资材部',self)
		self.check_pz=QCheckBox('品质部',self)
		self.check_jg=QCheckBox('加工厂',self)
		self.check_zz=QCheckBox('产品制造科',self)
		self.check_js=QCheckBox('生产技术科',self)
		self.check_yy=QCheckBox('计划运营科',self)

		self.li_checkbox=[]
		self.li_checkbox.append(self.check_yf)
		self.li_checkbox.append(self.check_zc)
		self.li_checkbox.append(self.check_pz)
		self.li_checkbox.append(self.check_jg)
		self.li_checkbox.append(self.check_zz)
		self.li_checkbox.append(self.check_js)
		self.li_checkbox.append(self.check_yy)
		self.check_finaly=QCheckBox('最终确认(勾选后将无法对该分析进行修改)',self)
		self.check_finaly.setCheckState(0)
		glayout=QGridLayout(self)
		self.check_wait_analysis=QCheckBox('原因待分析',self)
		self.check_wait_analysis.setCheckState(0)
		self.check_wait_analysis.stateChanged.connect(self.check_wait_analysis_event)


		glayout.addWidget(label_person,0,0)
		glayout.addWidget(self.lineedit_person,0,1,1,2)
		glayout.addWidget(label_person_quality,1,0)
		glayout.addWidget(self.lineedit_person_quality,1,1,1,2)
		glayout.addWidget(btn_add_name_quality,1,3,alignment=Qt.AlignRight)
		glayout.addWidget(label_duty_partment,1+1,0)
		glayout.addWidget(self.check_yf,1+1,1)
		glayout.addWidget(self.check_zc,1+1,2)
		glayout.addWidget(self.check_pz,1+1,3)
		glayout.addWidget(self.check_jg,2+1,0)
		glayout.addWidget(self.check_zz,2+1,1)

		glayout.addWidget(self.check_js,2+1,2)
		glayout.addWidget(self.check_yy,2+1,3)
		glayout.addWidget(label_result,3+1,0)
		glayout.addWidget(self.check_wait_analysis,3+1,1)
		glayout.addWidget(self.textedit_result,4+1,0,1,4)
		glayout.addWidget(btn_commit,5+1,3)
		glayout.addWidget(btn_add_name,0,3,alignment=Qt.AlignRight)
		glayout.addWidget(self.check_finaly,5+1,0,1,2)

		self.setLayout(glayout)
		self.show()

	def add_name_quality(self):
		winconfirm=WinConfirm()
		login_flag,name=winconfirm.get_result()
		if login_flag=='success':
			self.li_name_quality.append(name)
			self.lineedit_person_quality.setText(self.lineedit_person_quality.text()+'/'+name)

	def check_wait_analysis_event(self):
		if self.check_wait_analysis.checkState()==2:
			self.textedit_result.setPlainText('原因待分析')
			self.textedit_result.setReadOnly(True)
			self.check_finaly.setCheckState(0)
			self.check_finaly.setEnabled(False)
		if self.check_wait_analysis.checkState()==0:
			self.textedit_result.setPlainText('')
			self.textedit_result.setReadOnly(False)
			self.check_finaly.setCheckState(0)
			self.check_finaly.setEnabled(True)


	def add_name_event(self):
		winconfirm=WinConfirm()
		login_flag,name=winconfirm.get_result()
		if login_flag=='success':
			self.li_name.append(name)
			self.lineedit_person.setText(self.lineedit_person.text()+'/'+name)


	def commit_event(self):
		if len(self.li_name)==0:
			QMessageBox(text='   请添加确认人！  ',parent=self).show()
			return

		if self.check_finaly.checkState()==0:
			problem_plan_state='已分析'
		if self.check_finaly.checkState()==2:
			problem_plan_state='已完成'
		if self.check_wait_analysis.checkState()==2:
			problem_plan_state='原因待查'
		result=self.textedit_result.toPlainText()
		if result.replace(' ','')=='':
			return
		now=datetime.datetime.now()
		now=str(now)[0:19]
		cur.execute("update problem.problem_record set plan_state=%s where id=%s",(problem_plan_state,str(self.problem_id)))
		cur.execute("update problem.analysis set result_state='历史记录' where problem_id=%s",(self.problem_id))
		cur.execute("insert into problem.analysis (problem_id,result,result_state,commit_time) \
			values (%s,%s,%s,%s)",(str(self.problem_id),result,'最新记录',now))
		cur.execute("select max(id) from problem.analysis")
		analysis_id=cur.fetchall()[0][0]
		analysis_id=str(analysis_id)
		for i in self.li_name:
			cur.execute("insert into problem.analysis_person (analysis_id,confirm_person) \
				values (%s,%s)",(analysis_id,str(i)))
		for i in self.li_name_quality:
			cur.execute("insert into problem.analysis_person_quality (analysis_id,confirm_person,confirm_time) \
				values (%s,%s,%s)",(analysis_id,str(i),now))
		for i in self.li_checkbox:
			if i.checkState()==2:
				cur.execute("insert into problem.analysis_duty (analysis_id,partment) \
					values (%s,%s)",(analysis_id,str(i.text())))
		conn.commit()
		self.close()
		winmain.winnofinish.flush_view_detail(self.problem_id)

'''
显示全部的解决方案
'''
class WinViewSolve(QGroupBox):
	def __init__(self,problem_id):
		super().__init__('解决方案')
		self.problem_id=problem_id
		self.initUI()

	def initUI(self):
		vlayout=QVBoxLayout(self)
		cur.execute("select id from problem.solve_plan where problem_id=%s",(str(self.problem_id)))
		li=cur.fetchall()
		conn.commit()
		for i in li:
			vlayout.addWidget(WinViewSolveOnce(i[0],self.problem_id,self))
		if len(li)==0:
			vlayout.addWidget(WinViewSolveOnce(0,self.problem_id,self))
		self.setLayout(vlayout)
		self.show()


'''
显示一次的解决方案
'''
class WinViewSolveOnce(QWidget):
	def __init__(self,solve_id,problem_id,parent):
		super().__init__()
		self.solve_id=solve_id
		self.problem_id=problem_id
		self.parent=parent
		self.initUI()

	def initUI(self):
		self.btn_modify=QPushButton('修改',self)
		self.btn_add=QPushButton('添加',self)

		self.btn_modify.clicked.connect(self.modify_event)
		self.btn_add.clicked.connect(self.add_event)

		label_confirm_person=QLabel('确认人',self)
		label_commit_time=QLabel('提交时间',self)
		label_state=QLabel('状态',self)
		label_solve_plan=QLabel('解决方案(适用于本次)',self)
		label_material=QLabel('物料变化信息',self)
		label_split_way=QLabel('执行方案后的区分方法',self)

		label_crafts_change=QLabel('是否变更长期文件',self)
		self.label_crafts_content=QLabel('变更内容',self)
		self.label_crafts_person=QLabel('指定变更人',self)

		self.lineedit_confirm_person=QLineEdit(self)
		self.lineedit_commit_time=QLineEdit(self)
		self.lineedit_state=QLineEdit(self)
		self.textedit_solve_plan=QTextEdit(self)
		self.table=QTableWidget(0,7,self)
		self.lineedit_way_state=QLineEdit(self)
		self.textedit_judge_way=QTextEdit(self)

		self.lineedit_crafts_change=QLineEdit(self)
		self.lineedit_crafts_person=QLineEdit(self)
		self.textedit_crafts_content=QTextEdit(self)
		self.lineedit_crafts_person.setReadOnly(True)
		self.lineedit_crafts_change.setReadOnly(True)
		self.textedit_crafts_content.setReadOnly(True)


		self.lineedit_confirm_person.setReadOnly(True)
		self.lineedit_commit_time.setReadOnly(True)
		self.lineedit_state.setReadOnly(True)
		self.textedit_solve_plan.setReadOnly(True)
		self.lineedit_way_state.setReadOnly(True)
		self.textedit_judge_way.setReadOnly(True)
		self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.table.setHorizontalHeaderLabels(['分类','料号','名称','型号','数量','领料部门','确认人'])

		glayout=QGridLayout(self)

		glayout.addWidget(label_confirm_person,0,0)
		glayout.addWidget(self.lineedit_confirm_person,0,1,1,3)
		glayout.addWidget(label_commit_time,1,0)
		glayout.addWidget(self.lineedit_commit_time,1,1)
		glayout.addWidget(label_state,1,2)
		glayout.addWidget(self.lineedit_state,1,3)
		glayout.addWidget(label_solve_plan,2,0)
		glayout.addWidget(self.textedit_solve_plan,3,0,1,4)

		glayout.addWidget(label_crafts_change,4,0)
		glayout.addWidget(self.lineedit_crafts_change,4,1)
		glayout.addWidget(self.label_crafts_content,5,0)
		glayout.addWidget(self.textedit_crafts_content,6,0,1,4)
		glayout.addWidget(self.label_crafts_person,7,0)
		glayout.addWidget(self.lineedit_crafts_person,7,1,1,3)

		glayout.addWidget(label_material,3+1+4,0)
		glayout.addWidget(self.table,4+1+4,0,1,4)
		glayout.addWidget(label_split_way,5+1+4,0)
		glayout.addWidget(self.lineedit_way_state,5+1+4,1)
		glayout.addWidget(self.textedit_judge_way,6+1+4,0,1,4)
		glayout.addWidget(self.btn_modify,7+1+4,2)
		glayout.addWidget(self.btn_add,7+1+4,3,alignment=Qt.AlignRight)

		self.setLayout(glayout)
		self.show()
		self.load_data()

	def load_data(self):

		cur.execute("select solve_state,finish_state from problem.problem_record where id=%s",(str(self.problem_id)))
		li_state=cur.fetchall()[0]
		conn.commit()
		if li_state[1]=='未完成':
			if li_state[0]=='已完成':
				print('按钮不可用')
				self.btn_modify.setEnabled(False)
				self.btn_add.setEnabled(False)
		if li_state[1]=='已完成':
			self.btn_modify.setEnabled(False)
			self.btn_add.setEnabled(False)
		if self.solve_id==0:
			self.btn_modify.setEnabled(False)
			return


		cur.execute("select solve,plan_state,material_state,way_state,split_way,\
			confirm_time,crafts_state,crafts_content,crafts_person from problem.solve_plan \
			where id=%s",(self.solve_id))
		li=cur.fetchall()[0]
		conn.commit()
		
		if li[1]=='历史记录':
			self.btn_modify.setEnabled(False)
			self.btn_add.setEnabled(False)
		self.textedit_solve_plan.setPlainText(str(li[0]))
		self.lineedit_commit_time.setText(str(li[5]))
		self.lineedit_state.setText(str(li[1]))
		self.lineedit_way_state.setText(str(li[3]))
		self.textedit_judge_way.setPlainText(str(li[4]))

		self.btn_add.setEnabled(False)

		if li[2]=='无':
			self.table.hide()

		if li[3]=='不区分':
			self.textedit_judge_way.hide()

		if li[6]=='无变更':
			self.lineedit_crafts_change.setText('无变更')
			self.label_crafts_content.hide()
			self.label_crafts_person.hide()
			self.lineedit_crafts_person.hide()
			self.textedit_crafts_content.hide()

		if li[6]=='变更' or li[6]=='已完结':
			self.lineedit_crafts_change.setText('变更')
			self.lineedit_crafts_person.setText(li[8])
			self.textedit_crafts_content.setText(li[7])


		cur.execute("select confirm_person from problem.solve_person where plan_id=%s",(self.solve_id))
		li_temp=cur.fetchall()
		conn.commit()
		names=''
		for i in li_temp:
			names+='/'
			names+=i[0]
		self.lineedit_confirm_person.setText(names)

		if li[2]=='有':
			cur.execute("select operate_type,material_num,material_name,material_model,\
				material_count,partment,confirm_person from problem.solve_material where \
				plan_id=%s",(self.solve_id))
			li=cur.fetchall()
			conn.commit()
			self.table.setRowCount(len(li))
			rowcount=0
			for i in li:
				columncount=0
				for j in i:
					self.table.setItem(rowcount,columncount,QTableWidgetItem(str(j)))
					columncount+=1
				rowcount+=1

	def add_event(self):
		print('添加事件')
		self.winaddplan=WinCreateSolve(self.problem_id)

	def modify_event(self):
		self.winmodifysolve=WinModifySolve(self.solve_id,self.problem_id,self)
	




'''
创建解决方案
'''
class WinCreateSolve(QWidget):
	def __init__(self,problem_id):
		super().__init__()
		self.problem_id=problem_id
		self.li_name=[]
		self.initUI()

	def initUI(self):
		label_confirm_person=QLabel('确认人',self)
		label_solve_plan=QLabel('解决方案(必填)',self)
		label_material=QLabel('物料变化信息',self)
		label_judge_way=QLabel('执行方案后的区分方法',self)

		btn_add_name=QPushButton('添加确认人')
		btn_add_name.clicked.connect(self.add_name_event)
		btn_commit=QPushButton('提交',self)
		btn_commit.clicked.connect(self.commit_event)
		btn_add_material=QPushButton('添加物料',self)
		btn_add_material.clicked.connect(self.add_material_event)
		self.lineedit_person=QLineEdit(self)
		self.lineedit_person.setReadOnly(True)
		self.textedit_solve_plan=QTextEdit(self)
		self.textedit_judge_way=QTextEdit(self)
		self.textedit_judge_way.setReadOnly(True)
		self.table=QTableWidget(0,7)
		self.table.setHorizontalHeaderLabels(['分类','料号','名称','型号','数量','领料部门','确认人'])
		self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
		radiobtn_has_way=QRadioButton('作区分',self)
		radiobtn_has_way.clicked.connect(self.radiobtn_event)
		radiobtn_no_way=QRadioButton('不作区分',self)
		radiobtn_no_way.clicked.connect(self.radiobtn_event)
		radiobtn_no_way.setChecked(True)
		self.btn_group=QButtonGroup(self)
		self.btn_group.addButton(radiobtn_no_way,0)
		self.btn_group.addButton(radiobtn_has_way,1)
		self.check_finaly=QCheckBox('最终确认(勾选后将无法对该项进行修改)')
		self.check_finaly.setCheckState(0)

		self.check_crafts=QCheckBox('是否变更长期文件')
		self.check_crafts.setCheckState(0)
		self.check_crafts.stateChanged.connect(self.crafts_change_event)
		label_crafts_content=QLabel('变更内容',self)
		label_crafts_person=QLabel('指定变更人',self)
		self.textedit_crafts_content=QTextEdit(self)
		self.lineedit_crafts_person=QLineEdit(self)
		self.textedit_crafts_content.setReadOnly(True)
		self.lineedit_crafts_person.setReadOnly(True)




		glayout=QGridLayout(self)
		glayout.addWidget(label_confirm_person,0,0)
		glayout.addWidget(btn_add_name,1,3,alignment=Qt.AlignRight)
		glayout.addWidget(self.lineedit_person,1,0,1,3)
		glayout.addWidget(label_solve_plan,0+2,0)
		glayout.addWidget(self.textedit_solve_plan,1+2,0,1,4)

		glayout.addWidget(self.check_crafts,4,0,1,2)
		glayout.addWidget(label_crafts_content,5,0)
		glayout.addWidget(self.textedit_crafts_content,6,0,1,4)
		glayout.addWidget(label_crafts_person,7,0)
		glayout.addWidget(self.lineedit_crafts_person,7,1,1,3)

		glayout.addWidget(label_material,2+2+4,0)
		glayout.addWidget(btn_add_material,2+2+4,3,alignment=Qt.AlignRight)
		glayout.addWidget(self.table,3+2+4,0,1,4)
		glayout.addWidget(label_judge_way,4+2+4,0,1,2)
		glayout.addWidget(radiobtn_no_way,5+2+4,0)
		glayout.addWidget(radiobtn_has_way,5+2+4,1)
		glayout.addWidget(self.textedit_judge_way,6+2+4,0,1,4)
		glayout.addWidget(btn_commit,7+2+4,3,alignment=Qt.AlignRight)
		glayout.addWidget(self.check_finaly,9+4,0,1,3)

		self.setLayout(glayout)
	
		self.show()


	def crafts_change_event(self,state):
		if state==0:
			self.textedit_crafts_content.setPlainText('')
			self.textedit_crafts_content.setReadOnly(True)
			self.lineedit_crafts_person.setText('')
			self.lineedit_crafts_person.setReadOnly(True)
		if state==2:
			self.textedit_crafts_content.setReadOnly(False)
			self.lineedit_crafts_person.setReadOnly(False)


	def commit_event(self):
		if len(self.li_name)==0:
			QMessageBox(text='   请添加确认人！  ',parent=self).show()
			return
		conn.commit()
		if self.check_finaly.checkState()==0:
			problem_plan_state='已解决'
		if self.check_finaly.checkState()==2:
			problem_plan_state='已完成'
		now=str(datetime.datetime.now())[0:19]
		cur.execute("update problem.problem_record set solve_state=%s where id=%s",(problem_plan_state,str(self.problem_id)))
		cur.execute("update problem.solve_plan set plan_state='历史记录' where problem_id=%s",(self.problem_id))
		if self.btn_group.checkedId()==0:
			way_state='不区分'
			split_way=''
		else:
			way_state='区分'
			split_way=self.textedit_judge_way.toPlainText()

		plan=self.textedit_solve_plan.toPlainText()

		if self.table.rowCount()==0:
			material_state='无'
		else:
			material_state='有'

		if self.check_crafts.checkState()==2:
			crafts_state='变更'
			crafts_content=self.textedit_crafts_content.toPlainText()
			crafts_person=self.lineedit_crafts_person.text()
		if self.check_crafts.checkState()==0:
			crafts_state='无变更'
			crafts_content=''
			crafts_person=''

		cur.execute("insert into problem.solve_plan (problem_id,solve,material_state,way_state,\
			split_way,confirm_time,plan_state,crafts_state,crafts_content,crafts_person) values \
			(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(self.problem_id,plan,material_state,way_state,\
			split_way,now,'最新记录',crafts_state,crafts_content,crafts_person))

		cur.execute("select max(id) from problem.solve_plan")
		plan_id=cur.fetchall()[0][0]
		for i in self.li_name:
			cur.execute("insert into problem.solve_person (plan_id,confirm_person) values \
				(%s,%s)",(plan_id,i))

		if material_state=='有':
			for i in range(self.table.rowCount()):
				operate_type=self.table.item(i,0).text()
				material_num=self.table.item(i,1).text()
				material_name=self.table.item(i,2).text()
				material_model=self.table.item(i,3).text()
				material_count=self.table.item(i,4).text()
				partment=self.table.item(i,5).text()
				confirm_person=self.table.item(i,6).text()
				cur.execute("insert into problem.solve_material (plan_id,operate_type,material_num,\
					material_name,material_model,material_count,partment,confirm_person) values \
					(%s,%s,%s,%s,%s,%s,%s,%s)",(plan_id,operate_type,material_num,material_name,\
						material_model,material_count,partment,confirm_person))
		self.close()
		winmain.winnofinish.flush_view_detail(self.problem_id)

	def add_material_event(self):
		self.winaddmaterial=WinAddMaterial(self.table)

	def radiobtn_event(self):
		if self.btn_group.checkedId()==0:
			self.textedit_judge_way.setPlainText('')
			self.textedit_judge_way.setReadOnly(True)

		if self.btn_group.checkedId()==1:
			self.textedit_judge_way.setReadOnly(False)

	def add_name_event(self):
		winconfirm=WinConfirm()
		login_flag,name=winconfirm.get_result()
		if login_flag=='success':
			print('确认成功')
			self.li_name.append(name)
			self.lineedit_person.setText(self.lineedit_person.text()+'/'+name)


'''
添加物料界面
'''
class WinAddMaterial(QWidget):
	def __init__(self,table):
		super().__init__()
		self.table=table
		self.initUI()
	def initUI(self):
		label_type=QLabel('分类',self)
		label_material_num=QLabel('料号',self)
		label_material_name=QLabel('名称',self)
		label_material_model=QLabel('型号',self)
		label_material_count=QLabel('数量',self)
		label_material_partment=QLabel('领料部门',self)
		self.comb_type=QComboBox(self)
		self.comb_type.addItems(['增加','消耗'])
		self.lineedit_material_num=QLineEdit(self)
		self.lineedit_material_name=QLineEdit(self)
		self.lineedit_material_model=QLineEdit(self)
		self.lineedit_material_count=QLineEdit(self)
		self.lineedit_material_partment=QLineEdit(self)
		btn_commit=QPushButton('确定',self)
		btn_commit.clicked.connect(self.commit_event)

		glayout=QGridLayout(self)
		glayout.addWidget(label_type,0,0)
		glayout.addWidget(self.comb_type,0,1)
		glayout.addWidget(label_material_num,0,2)
		glayout.addWidget(self.lineedit_material_num,0,3)
		glayout.addWidget(label_material_name,1,0)
		glayout.addWidget(self.lineedit_material_name,1,1)
		glayout.addWidget(label_material_model,1,2)
		glayout.addWidget(self.lineedit_material_model,1,3)
		glayout.addWidget(label_material_count,2,0)
		glayout.addWidget(self.lineedit_material_count,2,1)
		glayout.addWidget(label_material_partment,2,2)
		glayout.addWidget(self.lineedit_material_partment,2,3)
		glayout.addWidget(btn_commit,3,3)

		self.setLayout(glayout)
		self.show()

	def commit_event(self):
		winconfirm=WinConfirm()
		login_flag,name=winconfirm.get_result()
		if login_flag=='success':
			print('table process')
			material_type=self.comb_type.currentText()
			material_num=self.lineedit_material_num.text()
			material_name=self.lineedit_material_name.text()
			material_model=self.lineedit_material_model.text()
			material_count=self.lineedit_material_count.text()
			material_partment=self.lineedit_material_partment.text()

			li=[]
			li.append(material_type)
			li.append(material_num)
			li.append(material_name)
			li.append(material_model)
			li.append(material_count)
			li.append(material_partment)
			li.append(name)

			rowcount=self.table.rowCount()
			self.table.setRowCount(self.table.rowCount()+1)
			
			columncount=0
			for i in li:
				self.table.setItem(rowcount,columncount,QTableWidgetItem(str(i)))
				columncount+=1

			self.close()


'''
修改解决方案
'''
class WinModifySolve(QWidget):
	def __init__(self,solve_id,problem_id,parent):
		super().__init__()
		self.parent=parent
		self.solve_id=solve_id
		self.problem_id=problem_id
		self.li_name=[]
		self.initUI()

	def initUI(self):
		label_confirm_person=QLabel('确认人',self)
		label_solve_plan=QLabel('解决方案(必填)',self)
		label_material=QLabel('物料变化信息',self)
		label_judge_way=QLabel('执行方案后的区分方法',self)

		btn_add_name=QPushButton('添加确认人')
		btn_add_name.clicked.connect(self.add_name_event)
		btn_commit=QPushButton('提交',self)
		btn_commit.clicked.connect(self.commit_event)
		btn_add_material=QPushButton('添加物料',self)
		btn_add_material.clicked.connect(self.add_material_event)
		self.lineedit_person=QLineEdit(self)
		self.lineedit_person.setReadOnly(True)
		self.textedit_solve_plan=QTextEdit(self)
		self.textedit_judge_way=QTextEdit(self)
		self.textedit_judge_way.setReadOnly(True)
		self.table=QTableWidget(0,7)
		self.table.setHorizontalHeaderLabels(['分类','料号','名称','型号','数量','领料部门','确认人'])
		self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
		action_delete=QAction('删除',self)
		action_delete.triggered.connect(self.delete_record)
		self.table.addAction(action_delete)
		self.table.setContextMenuPolicy(Qt.ActionsContextMenu)
		self.radiobtn_has_way=QRadioButton('作区分',self)
		self.radiobtn_has_way.clicked.connect(self.radiobtn_event)
		self.radiobtn_no_way=QRadioButton('不作区分',self)
		self.radiobtn_no_way.clicked.connect(self.radiobtn_event)
		self.radiobtn_no_way.setChecked(True)
		self.btn_group=QButtonGroup(self)
		self.btn_group.addButton(self.radiobtn_no_way,0)
		self.btn_group.addButton(self.radiobtn_has_way,1)
		self.check_finaly=QCheckBox('最终确认(勾选后将无法对该分析进行修改)')
		self.check_finaly.setCheckState(0)

		self.check_crafts=QCheckBox('是否变更长期文件')
		self.check_crafts.setCheckState(0)
		self.check_crafts.stateChanged.connect(self.crafts_change_event)
		label_crafts_content=QLabel('变更内容',self)
		label_crafts_person=QLabel('指定变更人',self)
		self.textedit_crafts_content=QTextEdit(self)
		self.lineedit_crafts_person=QLineEdit(self)

		glayout=QGridLayout(self)
		glayout.addWidget(label_confirm_person,0,0)
		glayout.addWidget(btn_add_name,1,3,alignment=Qt.AlignRight)
		glayout.addWidget(self.lineedit_person,1,0,1,3)
		glayout.addWidget(label_solve_plan,0+2,0)
		glayout.addWidget(self.textedit_solve_plan,1+2,0,1,4)

		glayout.addWidget(self.check_crafts,4,0,1,2)
		glayout.addWidget(label_crafts_content,5,0)
		glayout.addWidget(self.textedit_crafts_content,6,0,1,4)
		glayout.addWidget(label_crafts_person,7,0)
		glayout.addWidget(self.lineedit_crafts_person,7,1,1,3)

		glayout.addWidget(label_material,2+2+4,0)
		glayout.addWidget(btn_add_material,2+2+4,3,alignment=Qt.AlignRight)
		glayout.addWidget(self.table,3+2+4,0,1,4)
		glayout.addWidget(label_judge_way,4+2+4,0,1,2)
		glayout.addWidget(self.radiobtn_no_way,5+2+4,0)
		glayout.addWidget(self.radiobtn_has_way,5+2+4,1)
		glayout.addWidget(self.textedit_judge_way,6+2+4,0,1,4)
		glayout.addWidget(btn_commit,7+2+4,3,alignment=Qt.AlignRight)
		glayout.addWidget(self.check_finaly,9+4,0,1,3)

		self.setLayout(glayout)
		self.setMinimumWidth(600)
		self.show()
		self.load_data()

	def crafts_change_event(self,state):
		if state==0:
			self.textedit_crafts_content.setPlainText('')
			self.textedit_crafts_content.setReadOnly(True)
			self.lineedit_crafts_person.setText('')
			self.lineedit_crafts_person.setReadOnly(True)
		if state==2:
			self.textedit_crafts_content.setReadOnly(False)
			self.lineedit_crafts_person.setReadOnly(False)

	def delete_record(self):
		self.table.removeRow(self.table.currentRow())

	def add_material_event(self):
		self.winaddmaterial=WinAddMaterial(self.table)

	def radiobtn_event(self):
		if self.btn_group.checkedId()==0:
			self.textedit_judge_way.setPlainText('')
			self.textedit_judge_way.setReadOnly(True)

		if self.btn_group.checkedId()==1:
			self.textedit_judge_way.setReadOnly(False)
	def add_name_event(self):
		winconfirm=WinConfirm()
		login_flag,name=winconfirm.get_result()
		if login_flag=='success':
			print('确认成功')
			self.li_name.append(name)
			self.lineedit_person.setText(self.lineedit_person.text()+'/'+name)

	def load_data(self):
		if self.solve_id==0:
			self.btn_modify.setEnabled(False)
			return

		cur.execute("select solve,plan_state,material_state,way_state,split_way,\
			confirm_time,crafts_state,crafts_content,crafts_person from problem.solve_plan \
			where id=%s",(self.solve_id))
		li=cur.fetchall()[0]
		conn.commit()

		self.textedit_solve_plan.setPlainText(str(li[0]))
		if li[3]=='区分':
			self.radiobtn_has_way.setChecked(True)
			self.textedit_judge_way.setReadOnly(False)
		else:
			self.radiobtn_no_way.setChecked(True)
			self.textedit_judge_way.setReadOnly(True)
		self.textedit_judge_way.setPlainText(str(li[4]))

		if li[6]=='变更':
			self.check_crafts.setChecked(2)
			self.textedit_crafts_content.setPlainText(li[7])
			self.lineedit_crafts_person.setText(li[8])

		cur.execute("select confirm_person from problem.solve_person where plan_id=%s",(self.solve_id))
		li_temp=cur.fetchall()
		conn.commit()
		names=''
		for i in li_temp:
			names+='/'
			names+=i[0]
			self.li_name.append(i[0])
		self.lineedit_person.setText(names)


		#显示原来的物料表

		# if li[2]=='有':
		# 	cur.execute("select operate_type,material_num,material_name,material_model,\
		# 		material_count,partment,confirm_person from problem.solve_material where \
		# 		plan_id=%s",(self.solve_id))
		# 	li=cur.fetchall()
		# 	conn.commit()
		# 	self.table.setRowCount(len(li))
		# 	rowcount=0
		# 	for i in li:
		# 		columncount=0
		# 		for j in i:
		# 			self.table.setItem(rowcount,columncount,QTableWidgetItem(str(j)))
		# 			columncount+=1
		# 		rowcount+=1

	def commit_event(self):
		if len(self.li_name)==0:
			QMessageBox(text='   请添加确认人！  ',parent=self).show()
			return

		#将物料确认人添加到确认人表，有BUG
		# for i in range(self.table.rowCount()):
		# 	name=self.table.item(i,6).text()
		# 	if name not in self.li_name:
		# 		self.li_name.append(name)

		for i in self.li_name:
			winconfirm=WinConfirm(i)
			login_flag,name=winconfirm.get_result()
			if login_flag=='fail':
				QMessageBox(text='   操作已放弃！  ',parent=self).show()
				return
		conn.commit()
		if self.check_finaly.checkState()==0:
			problem_plan_state='已解决'
		if self.check_finaly.checkState()==2:
			problem_plan_state='已完成'
		cur.execute("update problem.problem_record set solve_state=%s where id=%s",(problem_plan_state,str(self.problem_id)))
		now=str(datetime.datetime.now())[0:19]
		cur.execute("update problem.solve_plan set plan_state='历史记录' where problem_id=%s",(self.problem_id))
		if self.btn_group.checkedId()==0:
			way_state='不区分'
			split_way=''
		else:
			way_state='区分'
			split_way=self.textedit_judge_way.toPlainText()

		plan=self.textedit_solve_plan.toPlainText()

		if self.table.rowCount()==0:
			material_state='无'
		else:
			material_state='有'

		if self.check_crafts.checkState()==2:
			crafts_state='变更'
			crafts_content=self.textedit_crafts_content.toPlainText()
			crafts_person=self.lineedit_crafts_person.text()
		if self.check_crafts.checkState()==0:
			crafts_state='无变更'
			crafts_content=''
			crafts_person=''

		cur.execute("insert into problem.solve_plan (problem_id,solve,material_state,way_state,\
			split_way,confirm_time,plan_state,crafts_state,crafts_content,crafts_person) values \
			(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(self.problem_id,plan,material_state,way_state,\
			split_way,now,'最新记录',crafts_state,crafts_content,crafts_person))

		cur.execute("select max(id) from problem.solve_plan")
		plan_id=cur.fetchall()[0][0]
		for i in self.li_name:
			cur.execute("insert into problem.solve_person (plan_id,confirm_person) values \
				(%s,%s)",(plan_id,i))

		if material_state=='有':
			for i in range(self.table.rowCount()):
				operate_type=self.table.item(i,0).text()
				material_num=self.table.item(i,1).text()
				material_name=self.table.item(i,2).text()
				material_model=self.table.item(i,3).text()
				material_count=self.table.item(i,4).text()
				partment=self.table.item(i,5).text()
				confirm_person=self.table.item(i,6).text()
				cur.execute("insert into problem.solve_material (plan_id,operate_type,material_num,\
					material_name,material_model,material_count,partment,confirm_person) values \
					(%s,%s,%s,%s,%s,%s,%s,%s)",(plan_id,operate_type,material_num,material_name,\
						material_model,material_count,partment,confirm_person))
		conn.commit()
		self.close()
		winmain.winnofinish.flush_view_detail(self.problem_id)

'''
显示工时
'''
class WinViewWorkHour(QGroupBox):
	def __init__(self,problem_id):
		super().__init__('工时信息')
		self.problem_id=problem_id
		self.initUI()

	def initUI(self):
		label_work=QLabel('工时信息',self)
		self.table=QTableWidget(0,6)
		self.table.setHorizontalHeaderLabels(['管理工时','技术工时','操作工时','线别','日期','确认人'])
		btn_add=QPushButton('添加',self)
		btn_add.clicked.connect(self.add_event)
		cur.execute("select finish_state from problem.problem_record where id=%s",(self.problem_id))
		finish_state=cur.fetchall()[0][0]
		if finish_state=='已完成':
			btn_add.setEnabled(False)
		glayout=QGridLayout(self)
		glayout.addWidget(label_work,0,0)
		glayout.addWidget(self.table,1,0,1,4)
		glayout.addWidget(btn_add,2,3,alignment=Qt.AlignRight)
		self.setLayout(glayout)
		self.show()
		self.flush_data()
		self.setMinimumWidth(500)

	def flush_data(self):
		cur.execute("select workhour_manage,workhour_technology,workhour_operate,line_name,\
			effect_date,confirm_person from problem.work_hour where problem_id=%s",(self.problem_id))
		li=cur.fetchall()
		conn.commit()
		self.table.setRowCount(len(li))
		rowcount=0
		for i in li:
			columncount=0
			for j in i:
				self.table.setItem(rowcount,columncount,QTableWidgetItem(str(j)))
				columncount+=1
			rowcount+=1

	def add_event(self):
		self.winaddworkhour=WinAddWorkHour(self.problem_id,self.table)


'''
添加工时
'''
class WinAddWorkHour(QWidget):
	def __init__(self,problem_id,table):
		super().__init__()
		self.problem_id=problem_id
		self.table=table
		self.initUI()

	def initUI(self):
		label_manage=QLabel('管理工时',self)
		label_technology=QLabel('技术工时',self)
		label_operate=QLabel('操作工时',self)
		label_line_name=QLabel('线别',self)
		label_date=QLabel('日期',self)

		self.lineedit_manage=QLineEdit(self)
		self.lineedit_technology=QLineEdit(self)
		self.lineedit_operate=QLineEdit(self)
		self.lineedit_line_name=QLineEdit(self)
		self.dateedit_effect_date=QDateEdit(QDate.currentDate(),self)

		btn_commit=QPushButton('确定',self)
		btn_commit.clicked.connect(self.commit_event)

		glayout=QGridLayout(self)
		glayout.addWidget(label_manage,0,0)
		glayout.addWidget(self.lineedit_manage,0,1)
		glayout.addWidget(label_technology,1,0)
		glayout.addWidget(self.lineedit_technology,1,1)
		glayout.addWidget(label_operate,2,0)
		glayout.addWidget(self.lineedit_operate,2,1)
		glayout.addWidget(label_line_name,3,0)
		glayout.addWidget(self.lineedit_line_name,3,1)
		glayout.addWidget(label_date,4,0)
		glayout.addWidget(self.dateedit_effect_date,4,1)
		glayout.addWidget(btn_commit,5,0,1,4,alignment=Qt.AlignCenter)

		self.setLayout(glayout)
		self.show()

	def commit_event(self):
		login_flag,name=WinConfirm().get_result()

		if login_flag=='fail':
			return
		now=datetime.datetime.now()
		now=str(now)[0:19]

		hour_manage=self.lineedit_manage.text()
		hour_technology=self.lineedit_technology.text()
		hour_operate=self.lineedit_operate.text()
		if hour_manage.replace(' ','')=='':
			hour_manage='0'
		if hour_technology.replace(' ','')=='':
			hour_technology='0'
		if hour_operate.replace(' ','')=='':
			hour_operate='0'
		line_name=self.lineedit_line_name.text()
		effect_date=self.dateedit_effect_date.date().toString("yyyy-MM-dd")

		cur.execute("insert into problem.work_hour (workhour_manage,workhour_technology,workhour_operate,line_name,\
			effect_date,confirm_person,confirm_time,problem_id) values (%s,%s,%s,%s,%s,%s,%s,%s)",(\
			hour_manage,hour_technology,hour_operate,line_name,effect_date,name,now,self.problem_id))
		conn.commit()
		print('添加成功')
		li=[]
		li.append(hour_manage)
		li.append(hour_technology)
		li.append(hour_operate)
		li.append(line_name)
		li.append(effect_date)
		li.append(name)
		rowcount=self.table.rowCount()
		self.table.setRowCount(rowcount+1)
		columncount=0
		for i in li:		
			self.table.setItem(rowcount,columncount,QTableWidgetItem(str(i)))
			columncount+=1
		self.close()



'''
提交异常记录
'''
class WinCreateProblem(QWidget):
	def __init__(self,parent):
		super().__init__()
		self.parent=parent
		self.initUI()

	def initUI(self):
		label_plan_id=QLabel('计划ID',self)
		label_model_main=QLabel('主型号',self)
		label_model=QLabel('系列号',self)
		label_batch=QLabel('批次',self)
		label_plan_count=QLabel('计划数量',self)
		label_happen_time=QLabel('发生时间',self)
		label_descript=QLabel('异常情况说明(此格内只填写1个异常问题，如是物料不良，写明料号、批号、流水号等信息)',self)
		label_stop_produce=QLabel('生产影响',self)
		label_problem_type=QLabel('问题分类',self)
		label_duty_person=QLabel('指定负责人',self)
		self.lineedit_plan_id=QLineEdit(self)
		self.lineedit_plan_id.editingFinished.connect(self.plan_num_event)
		self.lineedit_model_main=QLineEdit(self)
		self.lineedit_model=QLineEdit(self)
		self.lineedit_batch=QLineEdit(self)
		self.lineedit_count=QLineEdit(self)
		self.dateedit_happen_time=QDateTimeEdit(QDateTime.currentDateTime(),self)
		self.lineedit_duty_person=QLineEdit(self)
		self.textedit_descript=QTextEdit(self)
		self.comb_stop_produce=QComboBox(self)
		cur.execute("select effect_type from problem.produce_effect")
		li=cur.fetchall()
		conn.commit()
		li_effect=[]
		for i in li:
			li_effect.append(i[0])

		self.comb_stop_produce.addItems(li_effect)
		# self.comb_stop_produce.setEditable(True)
		self.comb_problem_type=QComboBox(self)
		cur.execute("select pro_type from problem.problem_type")
		li=cur.fetchall()
		conn.commit()
		li_type=[]
		for i in li:
			li_type.append(i[0])

		self.comb_problem_type.addItems(li_type)
		# self.comb_problem_type.setEditable(True)
		btn_commit=QPushButton('提交',self)
		btn_commit.clicked.connect(self.commit_event)

		glayout=QGridLayout(self)
		glayout.addWidget(label_plan_id,0,0)
		glayout.addWidget(self.lineedit_plan_id,0,1)
		glayout.addWidget(label_plan_count,0,2)
		glayout.addWidget(self.lineedit_count,0,3)
		glayout.addWidget(label_batch,1,0)
		glayout.addWidget(self.lineedit_batch,1,1)
		glayout.addWidget(label_model_main,1,2)
		glayout.addWidget(self.lineedit_model_main,1,3)
		glayout.addWidget(label_model,2,2)
		glayout.addWidget(self.lineedit_model,2,3)
		glayout.addWidget(label_happen_time,2,0)
		glayout.addWidget(self.dateedit_happen_time,2,1)
		glayout.addWidget(label_stop_produce,3,0)
		glayout.addWidget(self.comb_stop_produce,3,1)
		glayout.addWidget(label_problem_type,3,2)
		glayout.addWidget(self.comb_problem_type,3,3)
		glayout.addWidget(label_duty_person,3+1,0)
		glayout.addWidget(self.lineedit_duty_person,3+1,1)
		glayout.addWidget(label_descript,4+1,0,1,4)
		glayout.addWidget(self.textedit_descript,5+1,0,1,4)
		glayout.addWidget(btn_commit)

		self.setLayout(glayout)
		self.setWindowTitle('提交异常记录')
		self.show()

	def commit_event(self):
		plan_id=self.lineedit_plan_id.text()
		plan_count=self.lineedit_count.text()
		batch=self.lineedit_batch.text()
		main_model=self.lineedit_model_main.text()
		model=self.lineedit_model.text()
		happen_time=self.dateedit_happen_time.dateTime().toString('yyyy-MM-dd hh:mm')
		descript=self.textedit_descript.toPlainText()
		duty_person=self.lineedit_duty_person.text()
		now=datetime.datetime.now()
		now=str(now)[0:19]
		stop_produce=self.comb_stop_produce.currentText()
		problem_type=self.comb_problem_type.currentText()
		login_flag,name=WinConfirm().get_result()

		print(login_flag,name)
		print('窗口运行完成后')

		if login_flag=='fail':
			return

		cur.execute("select flow_num from problem.problem_record where id=(select max(id) \
			from problem.problem_record)")
		try:
			flow_num_max=cur.fetchall()[0][0]
			d=str(datetime.datetime.now())
			if flow_num_max[0:4]==d[2:4]+d[5:7]:
				s=str(int(flow_num_max[4:])+1)
				flow_num=flow_num_max[0:4]+s
			else:
				flow_num=d[2:4]+d[5:7]+'1'
		except:
			d=str(datetime.datetime.now())
			flow_num=d[2:4]+d[5:7]+'1'

		cur.execute("insert into problem.problem_record (main_model,model,project_id,batch_num,project_count,\
			happen_time,descript,person,commit_time,flow_num,plan_state,solve_state,duty_person,finish_state,\
			duty_person2,stop_produce,problem_type2) values (%s,%s,%s,%s,%s,%s,\
			%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(main_model,model,plan_id,batch,plan_count,happen_time,\
			descript,name,now,flow_num,'待处理','待处理',duty_person,'未完成','',stop_produce,problem_type))
		conn.commit()
		print('创建成功')
		QMessageBox(text='   创建成功！  ',parent=self).show()
		self.close()
		self.parent.flush_event()

	def plan_num_event(self):
		if re.match(r'^[\s]{0,}$',self.lineedit_plan_id.text()):
			return
		if self.lineedit_plan_id.isModified():
			self.lineedit_plan_id.setModified(False)
		else:
			return
		s=self.lineedit_plan_id.text()+'MD5'+self.lineedit_plan_id.text()+'dj'

		m=hashlib.md5(s.encode('ascii')).hexdigest()
		print(m)
		s='http://192.168.30.230/jiekou/OrderInfoGet_ById/?id='+self.lineedit_plan_id.text()+'&CheckCode='+m
		try:
			r=requests.get(s,timeout=2)
		except:
			QMessageBox(text='   数据获取失败！  ',parent=self).show()
			return
		j=r.json()
		if len(j)==0:
			self.lineedit_model_main.setText('')
			self.lineedit_model.setText('')
			self.lineedit_batch.setText('')
			self.lineedit_count.setText('')
			QMessageBox(text='   查询不到该计划id！  ',parent=self).show()
			return

		li=j[0]
		
		self.lineedit_model_main.setText(li['主型号'])
		self.lineedit_model.setText(li['型号'])
		self.lineedit_batch.setText(li['生产批次'])
		self.lineedit_count.setText(str(li['生产数量']))
		self.textedit_descript.setFocus()


'''
对用户密码进行确认
'''
class WinConfirm(QDialog):
	def __init__(self,defult_name=''):
		super().__init__()
		self.defult_name=defult_name
		self.initUI()

	def initUI(self):
		self.name=''
		self.login_flag='fail'
		label_name=QLabel('姓名',self)
		label_password=QLabel('密码',self)
		self.lineedit_name=QLineEdit(self)
		self.lineedit_name.setText(self.defult_name)
		self.lineedit_password=QLineEdit(self)
		self.lineedit_password.setEchoMode(QLineEdit.Password)
		if self.defult_name!='':
			self.lineedit_name.setReadOnly(True)
			self.lineedit_password.setFocus()
		btn_commit=QPushButton('确定',self)
		btn_commit.clicked.connect(self.commit_event)
		btn_new=QPushButton('创建新用户',self)
		btn_new.clicked.connect(self.new_event)
		glayout=QGridLayout(self)
		glayout.addWidget(label_name,0,0)
		glayout.addWidget(self.lineedit_name,0,1)
		glayout.addWidget(label_password,1,0)
		glayout.addWidget(self.lineedit_password,1,1)
		glayout.addWidget(btn_new,2,0,alignment=Qt.AlignCenter)
		glayout.addWidget(btn_commit,2,1,alignment=Qt.AlignCenter)
		
		self.setWindowModality(Qt.ApplicationModal)

		self.show()
		self.exec()

	def commit_event(self):
		name=self.lineedit_name.text()
		if name=='':
			return
		self.name=name
		password=self.lineedit_password.text()
		cur.execute("select * from problem.user_a where name=%s",(name))
		li_user=cur.fetchall()
		conn.commit()
		if len(li_user)==0:
			self.login_flag='fail'
			self.lineedit_password.setText('')
			self.lineedit_password.setPlaceholderText(u'用户名或密码错误')
			return
		if bcrypt.checkpw(password.encode('ascii'),li_user[0][2].encode('ascii')):
			print('登录成功')
			self.login_flag='success'
		else:
			self.login_flag='fail'
			self.lineedit_password.setText('')
			self.lineedit_password.setPlaceholderText(u'用户名或密码错误')
			return
		self.close()

	def get_result(self):
		return self.login_flag,self.name

	def new_event(self):
		global adduser
		self.close()
		adduser=AddUser()

'''
添加用户
'''
class AddUser(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		label_name=QLabel('姓名：',self)
		label_password=QLabel('密码：',self)
		label_partment=QLabel('密码：',self)
		self.line_edit_name=QLineEdit(self)
		self.line_edit_password=QLineEdit(self)
		self.line_edit_partment=QLineEdit(self)
		self.line_edit_password.setEchoMode(QLineEdit.Password)
		self.line_edit_partment.setEchoMode(QLineEdit.Password)  
		btn=QPushButton('确认添加',self)
		btn.clicked.connect(self.btn_event)

		glayout=QGridLayout(self)
		glayout.addWidget(label_name,0,0)
		glayout.addWidget(label_password,1,0)
		glayout.addWidget(label_partment,2,0)

		glayout.addWidget(self.line_edit_name,0,1)
		glayout.addWidget(self.line_edit_password,1,1)
		glayout.addWidget(self.line_edit_partment,2,1)
		glayout.addWidget(btn,3,0,1,2)

		self.show()

	def btn_event(self):
		name=self.line_edit_name.text()
		password=self.line_edit_password.text()
		partment=self.line_edit_partment.text()

		if re.match(r'^[\s]{0,}$',name):
			return
		cur.execute("select * from problem.user_a where name=%s",(name))
		li=cur.fetchall()
		if len(li)>0:
			QMessageBox(text='   用户名已存在！   ',parent=self).show()
			return

		if re.match(r'^[\s]{0,}$',password):
			return
		if re.match(r'^[\s]{0,}$',partment):
			return

		if password!=partment:
			QMessageBox(text='   密码不一致！   ',parent=self).show()
			return
		hashpw=bcrypt.hashpw(password.encode('ascii'),bcrypt.gensalt())
		try:
			cur.execute("insert into problem.user_a (name,password) values (%s,%s)",(name,hashpw))
			conn.commit()
			self.close()
			QMessageBox(text='   录入成功！   ',parent=self).show()
		except:
			QMessageBox(text='   录入失败！   ',parent=self).show()
			return


def connDB():
	# conn=pymssql.connect(host='192.168.70.3',user='Chenyong',password='147258',database='WeiXiuDB',charset='utf8')
	conn=pymysql.connect(host='127.0.0.1',user='root',password='000000',db='problem',charset='utf8')
	cur=conn.cursor()
	print('connect OK')
	return(conn,cur)

if __name__=='__main__':
	global version
	conn,cur=connDB()
	app=QApplication(sys.argv)
	version='1.63'
	run_flag=True

	cur.execute("select version_num_l,version_num_h from problem.version_control")
	li=cur.fetchall()
	conn.commit()
	version_l=float(li[0][0])
	version_h=float(li[0][1])
	version_curr=float(version)
	q=QWidget()
	if version_curr<version_l:
		QMessageBox(text='   软件版本过低,请选择最新版本！  ',parent=q).show()
		run_flag=False
	if version_curr>=version_h:
		QMessageBox(text='   由于该版本存在严重缺陷,请使用低版本软件！  ',parent=q).show()
		run_flag=False

	if run_flag:
		winmain=WinMain()
	sys.exit(app.exec_())