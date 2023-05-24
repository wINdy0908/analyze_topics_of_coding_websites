import mysql.connector
from mysql.connector import MySQLConnection, Error
from db_config import read_db_config
import re
import os
from collections import Counter
from db_search import company_name,difficulty,topic,cursor_execute,recommand_problem_with_company
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

##calculate number of distinct company in leetcode, interviewbit, codechef
def get_company_number(company):
    query=(f"""SELECT company_name From {company}_company""")
    val=cursor_execute(query)
    return(Counter(val))
    
    
##calculate the number of appearance of each problem 
def get_problem_number(company):
    query=(f"""select title_slug from {company}_company""")
    val=cursor_execute(query)
    return(Counter(val))

def distinct_problem_number(company):
    query=(f"select distinct title_slug from {company}_problem")
    val=cursor_execute(query)
    df=pd.DataFrame(val)
    return(len(df.index))

def plot_distinct_problem_number():
    plt.bar(["interviewbit","leetcode","codechef"],[distinct_problem_number("interviewbit"),distinct_problem_number("leetcode"),distinct_problem_number("codechef")],width=0.4)
    plt.title("number of problems in each website")
    plt.savefig("/Users/windy8810/Documents/GitHub/interview_problems_project/src/db/num_of_problem.png",bbox_inches='tight')
    plt.show()

#top 20 company in leetcode and interviewbit based on problem tags
#top 20 problem that 
def hist():
    interviewbit=get_company_number("interviewbit")
    interviwebit_rv=dict(sorted(interviewbit.items(), key=lambda x:x[1],reverse=True))

    leetcode=get_company_number("leetcode")
    leetcode_rv=dict(sorted(leetcode.items(), key=lambda x:x[1],reverse=True))

    

    plt.rcParams["figure.figsize"] = [12,10]
    plt.subplots_adjust(hspace=0.5)
    plt.subplot(1,2,1)
    plt.bar(list(interviwebit_rv.keys())[0:20],list(interviwebit_rv.values())[0:20],width=0.4)
    plt.title("interviewbit top 20 companies")
    plt.xticks(rotation = 90)
    plt.subplot(1,2,2)
    plt.bar(list(leetcode_rv.keys())[0:20],list(leetcode_rv.values())[0:20],width=0.4)
    plt.title("leetcode top 20 comanies")
    plt.xticks(rotation = 90)
    plt.savefig("/Users/windy8810/Documents/GitHub/interview_problems_project/src/db/company_website.png",bbox_inches='tight')
    plt.show()

def hist2():
    interviewbit_problem=get_problem_number("interviewbit")
    inter_pl_rv=dict(sorted(interviewbit_problem.items(), key=lambda x:x[1],reverse=True)) #sort problem by number of occurances of problem from hifh to low 

    leetcode_problem=get_problem_number("leetcode")
    leet_pl_rv=dict(sorted(leetcode_problem.items(), key=lambda x:x[1],reverse=True))

    plt.rcParams["figure.figsize"] = [12,10]
    plt.subplots_adjust(hspace=0.5)
    plt.subplot(1,2,1)
    plt.bar(list(inter_pl_rv.keys())[0:20],list(inter_pl_rv.values())[0:20],width=0.4)
    plt.xticks(rotation = 90)
    plt.title("interviewbit top 20 problems")
    plt.subplot(1,2,2)
    plt.bar(list(leet_pl_rv.keys())[0:20],list(leet_pl_rv.values())[0:20],width=0.4)
    plt.title("leetcode top 20 problems")
    plt.xticks(rotation = 90)
    plt.savefig("/Users/windy8810/Documents/GitHub/interview_problems_project/src/db/problem_website.png",bbox_inches='tight')
    plt.show()

    
######
######

def data_acrate_difficulty(company):
    db_config = read_db_config()
    if company=="codechef":
        query_codechef=(f"""SELECT difficulty,total_accepted*100/total_sub as result from 
        codechef_problem where difficulty in ("easy","medium","hard","challenge")""")
        with MySQLConnection(**db_config) as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(query_codechef)
                    results=cursor.fetchall()
                    ans=pd.DataFrame(results, columns =['difficulty',"ac_rate"])
                    ans=ans.replace("challenge","hard")
        
                    return(ans)
                except Error as e:
                    print(e)
 
    else:
        if company=="interviewbit":
            query=(f"""select difficulty,ac_rate*100 from problem_connect.{company}_problem where difficulty in ("easy","medium","hard")""")
        else:
            query=(f"""select difficulty,ac_rate from problem_connect.{company}_problem where difficulty in ("easy","medium","hard")""")

        with MySQLConnection(**db_config) as conn:
            with conn.cursor() as cursor:
                try:
                    # a=[]
                    # b=[]
                    cursor.execute(query)
                    results=cursor.fetchall()
                    ans=pd.DataFrame(results,columns=["difficulty","ac_rate"])
                    
                    return(ans)
                except Error as e:
                    print(e)
   
def mean_ac_group_by_diff(company):
    ans=data_acrate_difficulty(company).groupby(["difficulty"]).mean()
    if "easy" in ans.index:
        response=[company,ans.loc['easy'][0],ans.loc['medium'][0],ans.loc['hard'][0]]
    else:
        response=[company,ans.loc['Easy'][0],ans.loc['Medium'][0],ans.loc['Hard'][0]]
    return(response)

###line plot regarding mean accuracy rate among three website
def diff_ac_copmany():
    df=pd.DataFrame({"company":[0,0,0],"easy":[0,0,0],"medium":[0,0,0],"hard":[0,0,0]})
    df.iloc[0]=mean_ac_group_by_diff("codechef")
    df.iloc[1]=mean_ac_group_by_diff("leetcode")
    df.iloc[2]=mean_ac_group_by_diff("interviewbit")
    df=df.set_index('company')
    ax=df.T.plot(figsize=(7,6))
    ax.set_xlabel("difficulty",fontsize=12)
    ax.set_ylabel("acceptance rate",fontsize=12)
    plt.savefig('/Users/windy8810/Documents/GitHub/interview_problems_project/src/db/line_plot.png')
    plt.show()

######
######
#problem type for interviewbit
def topic_company(company):
    query=(f"""select {company}_topic.topic_name, {company}_company.company_name from problem_connect.{company}_topic, problem_connect.{company}_company 
    where problem_connect.{company}_company.id in (SELECT id FROM problem_connect.{company}_topic)""")
    db_config = read_db_config()
    with MySQLConnection(**db_config) as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(query)
                    result=cursor.fetchall()
                    result=pd.DataFrame(result)
                    result=result.dropna()
                    result.columns=["topic","company"]
                    value=Counter(result["topic"])
                    value_rv=dict(sorted(value.items(),key=lambda x:x[1],reverse=True))
                    x=list(value_rv.keys())[0:10]
                    y=list(value_rv.values())[0:10]
                    print(x,y)
                    return(x,y)
                    
                   
                except Error as e:
                    print (e)


def topic(website):
    query=(f"select topic_name from {website}_topic")
    db_config = read_db_config()
    ans=cursor_execute(query)
    value=Counter(ans)
    value_rv=dict(sorted(value.items(),key=lambda x:x[1],reverse=True))
    x=list(value_rv.keys())[0:10]
    y=list(value_rv.values())[0:10]
    print(x,y)
    return(x,y)

    



#top 10 topics of problem that website used most often
def barplot():
    plt.rcParams["figure.figsize"] = [20,18]
    
    plt.subplots_adjust(hspace=0.3)
    plt.subplot(3,1,1)
    a,b=topic_company("interviewbit")
    plt.title(f"top 10 problem topics used most often by companies in interviewbit ")
    plt.barh(a,b)
    plt.yticks(fontsize = 10)
    
    

    plt.subplot(3,1,2)
    a,b=topic_company("leetcode")
    plt.title(f"top 10 problem topics used most often by companies in leetcode ")
    plt.barh(a,b)
    plt.yticks(fontsize = 10)

    plt.subplot(3,1,3)
    a,b=topic("codechef")
    plt.title(f"top 10 problem topics show most often in codechef ")
    plt.barh(a,b)
    plt.yticks(fontsize = 10)
    
    #image_path="/Users/windy8810/Documents/GitHub/interview_problems_project/src/db"
    plt.savefig("/Users/windy8810/Documents/GitHub/interview_problems_project/src/db/barplot.png")
    plt.show()


if __name__ == "__main__":
    diff_ac_copmany() #line_plot.png
    #plot_distinct_problem_number()#plot_distinct_problem_number
    #barplot() #barplot.png top 10 topics of problem that website used oftenly
    #hist()#company_website.png
    #hist2()#problem_website.png
   
    
    
    