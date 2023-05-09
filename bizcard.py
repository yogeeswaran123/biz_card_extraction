import os
import streamlit as st
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
import easyocr
import cv2 as cv
import mysql.connector as mc
from PIL import Image

#Cache is used to avoid the re-running of the functions
@st.cache_data
def extractor(link):
    data=["null"]
    reader = easyocr.Reader(["en"])
    result = reader.readtext(link)
    for i in result:
        #print(i)
        #print(type(i))
        for j in i:
            if type(j) == type('srt'): # easyocr returns boundry,string and confidence score, from that only string is extracted
                #st.write(j)
                #print(type(j))
                data.append(j)               
    return data # returned list contains data of the business card in list format

# main page which shows a sample image
st.title(":blue[DIGITAL BUSINESS CARD HOLDER]")
image = Image.open(r"C:\Users\yogesh\Desktop\opencv\logo1.jpg")
st.image(image)
add_sel_box= st.sidebar.title(":orange[PLEASE SELECT THE MODE]")
link = st.text_input(":red[INSERT BUSINESS CARD IMAGE] :green[(PATH)]",value=r"C:\Users\yogesh\Desktop\opencv\biz.png") #link is path of the business card image, type or past the path of the file

#below code impliments side bar which uses radio button to select the process either to extract the business card or to view the stored card
add_sel_box= st.sidebar.radio("Bussiness Card Extraction",("BUSINESS CARD EXTRACTOR","VIEW STORED CARDS"), key="radio")


# This code block is for extracting a business card
if st.session_state.radio == "BUSINESS CARD EXTRACTOR": #from side bar if business_card_extraction radio button is clicked, session_state changes to business_card_extraction
    st.title(":blue[Bussiness Card Extraction]")


# function blocked is called, link is obtained manually     
    card_data = extractor(link)

    st.header("CARD DETAILS")
    st.write("BUSINESS CARD CONTAIN FOLLOWING DETAILS")
    st.write(list(card_data))

    st.subheader("SELECT THE APPROPRIATE DATA")
    #select box is used to get the appropriate values, those are output of the function block "extractor", it is in list format
    name = st.selectbox("SELECT THE NAME",card_data,key="name")
    #st.write(name)

    designation = st.selectbox("SELECT THE DESIGNATION",card_data,key="designation")
    #st.write(designation)

    company = st.selectbox("SELECT THE COMPANY NAME",card_data,key="compani")
    #st.write(company)

    contact_number_1 = st.selectbox("SELECT THE CONTACT NUMBER_1",card_data,key="contact_number_1")
    #st.write(contact_number_1)

    contact_number_2 = st.selectbox("SELECT THE CONTACT NUMBER_2",card_data,key="contact_number_2")
    #st.write(contact_number_2)

    mail_id = st.selectbox("SELECT THE MAIL_ID",card_data,key="mail_id")
    #st.write(mail_id)

    address = st.multiselect("please select the address",card_data,key="address")
    st.write(address)
    #this block is used to deal with the backslash(escape character), string.replace method is used
    link_re=link.replace("\\","\\\\\\\\")
    #st.write(link)
    #st.write(link_re)

    #mysql database is used, mysql.connector module is used for making connections
    mydb = mc.connect(host="localhost", user="root", password="yogi123",database="business_cards")
    cur = mydb.cursor()
    #f-string/formatted string is used to generate the insert query
    query_to_insert_data = f"""insert into imp_biz_card_details (name, designation, company, contact_number_1, contact_number_2, mail_id, address, card_link)
                values (\"{name}\",\"{designation}\",\"{company}\",\"{contact_number_1}\",\"{contact_number_2}\",\"{mail_id}\",\"{address}\",\"{link_re}\")"""
    #st.write(query)
    # this if block is used to load the business card data to mysql database, database="business_cards", table="imp_biz_card_details"
    if st.button("send to DB",key="db"):
        st.write(st.session_state.db)# == True:
        cur.execute(query_to_insert_data)
        mydb.commit()
        mydb.close()
        st.success('BUSINESS CARD UPLOADED TO DB', icon="✅")
####################################################################################
        
#if radio button from the side changed to view_stored_cards, session_state of the block changes to view_stored_cards, this block gets executed
if st.session_state.radio == "VIEW STORED CARDS":
    
    #this code block is to retrive data
    #this code connect to mysql database and fetch the results
    mydb = mc.connect(host="localhost", user="root", password="yogi123",database="business_cards")
    cur = mydb.cursor()
    cur.execute("select name from imp_biz_card_details")
    list_of_names=cur.fetchall() #fetchall returns data in list of tuples of each row [(row1),(row2)...(row n)]
    #st.write(list_of_names)
    new_list=[]
    for i in range(0,len(list_of_names)): #form the fetchall() result names are obtained which is given as input to input variable selectbox
        #st.write(len(list_of_names))
        x = list_of_names[i][0]
        #st.write(x)
        new_list.append(x)
    #st.write(new_list)
    input=st.selectbox("please select the name",new_list)
    st.write(input)
    selection_query = f"select * from imp_biz_card_details where name =\"{input}\"" #this query will select the data from database which matchs the where clause
    cur.execute(selection_query)
    data=cur.fetchall()
    #this block will display the data of individual business card with their image
    name=''
    cont_number=''
    for i in data: # data is list format
        #st.write(data)
        #st.write(i)
        name=f"name : {i[0]}"
        col1,col2=st.columns(2,gap="large")
        with col1: # this display the details
            st.header("Details")
            name=f"Name : {i[0]}"
            st.write(name)
            
            Designation=f"Designation : {i[1]}"
            st.write(Designation)
            
            Company=f"Company : {i[2]}"
            st.write(Company)
            
            Contact_Number_1=f"Contact_Number_1 : {i[3]}"
            st.write(Contact_Number_1)
            
            mail_id=f"mail_id : {i[5]}"
            st.write(mail_id)
        with col2: # this display the image
            st.header("BUSINESS_CARD")
            link = i[7]
            image = Image.open(fr"{link}")
            st.image(image, caption='Stored_Image')
            #st.write(link)
            # delete query
            # this block provides a button to delete the record from the data base
            if st.button("DELETE"):
                query=f"delete from imp_biz_card_details where name=\"{i[0]}\""
                cur.execute(query)
                mydb.commit()
                st.success('BUSINESS_CARD IS DELETED FROM DB', icon="✅")
                
#  block to fetch the no of records and display in sidebar
with st.sidebar:
    mydb = mc.connect(host="localhost", user="root", password="yogi123",database="business_cards")
    cur = mydb.cursor()
    qurey_to_count_nof_records = "select count(*) from imp_biz_card_details"
    # the above query fetches the no of records in the database which is equal to no of business cards
    cur.execute(qurey_to_count_nof_records)
    no_of_cards = cur.fetchone()
    st.write("TOTAL NO OF BUSINESS CARS IN :", no_of_cards[0])
    st.write(no_of_cards)      
        
      
        







