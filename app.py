from flask import Flask, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_restful import Resource, Api, request
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'S243t154shd$gu/adafhfj*jhDSHHDfbbfamfj_dAJDA.VVFAEF766r6^&'
jwt = JWTManager(app)
api = Api(app)

client = MongoClient()
client = MongoClient('mongodb+srv://admin:admin@cluster0.cgjex.gcp.mongodb.net/test?retryWrites=true&w=majority')
print("Mongodb connection succesfull")

#admin controls
db = client['admin_database']
class Admin_auth(Resource):
    def post(self):
        data = request.get_json()
        admins = db.admins.find()
        if data['username']==None:
            return {"message":"email field is empty"}, 400
        if data['pass']==None:
            return {"message":"password field is empty"}, 400
        res = next(filter(lambda x: (x['username']==data['username'] and x['pass']== data['pass']), admins),None)
        if res is None:
            return {"message":"admin user not found"}, 404
        if data['username']==res['username'] and data['pass']==res['pass']:
            access_token = create_access_token(identity={"username":res['username']})
            return {"access_token":access_token}, 200
        else:
            return {"message":"Invalid login credentials"}, 400

class Admin(Resource):

    def get(self):
        result = db.admins.find()
        ad=[]
        for admin in result:
            ad.append({
                "name":admin['name'],
                "username":admin['username'],
                "pass":admin['pass']
            })
        if len(ad) == 0:
            return {"message":"no data found"}, 404
        return ad


    def post(self,name):
        data = request.get_json()
        admin ={ 
            "name": name,
            "username":data["username"],
            "pass":data["pass"]
        }
        if name=='admin':
            return {"message":"Cant add admin user with name {}".format(name)}, 404
        res = db.admins.insert_one(admin)
        if res:
            return {"Sucess":"Entered new admin"}, 200


    def delete(self,name):
        admins = db.admins.find()
        res = next(filter(lambda x: x['name']==name,admins),None)
        if res != None and name != 'admin':
            db.admins.delete_one(
                {"name":name}
            )
            return {"message":"deleted sucessfully"},200
        else:
            return {"message":"Not found"}, 404

tdb=client['teacher_database']
class Teacher(Resource):

    def post(self,name):
        data = request.get_json()
        results = tdb.teachers.find()
        if next(filter(lambda x: x['name']==name ,results),None):
            return {'message':"An item with name '{}' already exists".format(name)}, 400
        teacher = {
            "name": name,
            "designation": data['designation'],
            "username": data['username'],
            "pass":data['pass'],
            "email":data['email'],
            "phone":data['phone']
        }
        res = tdb.teachers.insert_one(teacher)
        if res:
            return {"success":"Entered new User"},200


    def get(self):
        results = tdb.teachers.find()
        teachers = []
        for teacher in results:
            teachers.append({
                "name": teacher['name'],
                "designation": teacher['designation'],
                "username": teacher['username'],
                "pass":teacher['pass'],
                "email":teacher['email'],
                "phone":teacher['phone']
            })
        if len(teachers) == 0:
            return {"message":"no data found"}, 404
        return teachers, 200


    def put(self,name):
        data = request.get_json()
        teachers = tdb.teachers.find()
        teacher = next(filter(lambda x: x['name']==name,teachers),None)
        if teacher is None:
            teacher = {
                "name": name,
                "designation": data['designation'],
                "username": data['username'],
                "pass":data['pass'],
                "email":data['email'],
                "phone":data['phone']
            }
            res = tdb.teachers.insert_one(teacher)
            return {"Message":"Inserted sucessfully"},200
        else:
            tdb.teachers.update(
                { 
                    "name": name 
                },
                {
                    "name": name,
                    "designation": data['designation'],
                    "username": data['username'],
                    "pass":data['pass'],
                    "email":data['email'],
                    "phone":data['phone']
                },
            )
            return {"message":"updated"},200


    def delete(self,name):
        teachers = tdb.teachers.find()
        res = next(filter(lambda x: x['name']==name,teachers),None)
        if res != None:
            tdb.teachers.delete_one(
                {"name":name}
            )
            return {"message":"deleted sucessfully"},200
        else:
            return {"message":"Not found"}, 404
#admin controls

#teachers login controls
class Teachers_auth(Resource):
    def post(self):
        data = request.get_json()
        teachers = tdb.teachers.find()
        if data['username']==None:
            return {"message":"email field is empty"}, 400
        if data['pass']==None:
            return {"message":"password field is empty"}, 400
        res = next(filter(lambda x: (x['username']==data['username'] and x['pass']== data['pass']), teachers),None)
        if res is None:
            return {"message":"teacher user not found"}, 404
        if data['username']==res['username'] and data['pass']==res['pass']:
            access_token = create_access_token(identity={"username":res['username']})
            return {"access_token":access_token}, 200
        else:
            return {"message":"Invalid login credentials"}, 400
#teachers login controls

#teacher controls
class Student(Resource):

    def post(self,branch,year):
        st_db=client[branch]
        data = request.get_json()
        collection_name = year
        results = st_db[collection_name].find()
        if next(filter(lambda x: x['usn']==data['usn'] ,results),None):
            return {'message':"An item with usn '{}' already exists".format(data['usn'])}, 400
        student = {
            "name":data['name'],
            "mail_id":data['mail_id'],
            "usn":data['usn'],
            "phone_no":data['phone_no'],
            "branch":data['branch'],
            "vtu_result":data['vtu_result'],
            "year":year,
            "p1_basics":[{
                    'mark_obtained':data['p1_basics'][0]['mark_obtained'],
                    'pass_mark':data['p1_basics'][0]['pass_mark'],
                    'pass': check_pass(data['p1_basics'][0]['mark_obtained'],data['p1_basics'][0]['pass_mark'])
            }],
            "p2_c":[{
                    'mark_obtained':data['p2_c'][0]['mark_obtained'],
                    'pass_mark':data['p2_c'][0]['pass_mark'],
                    'pass': check_pass(data['p2_c'][0]['mark_obtained'],data['p2_c'][0]['pass_mark'])
            }],
            "p2_python":[{
                    'mark_obtained':data['p2_python'][0]['mark_obtained'],
                    'pass_mark':data['p2_python'][0]['pass_mark'],
                    'pass': check_pass(data['p2_python'][0]['mark_obtained'],data['p2_python'][0]['pass_mark'])
            }],
            "p2_advance":[{
                    'mark_obtained':data['p2_advance'][0]['mark_obtained'],
                    'pass_mark':data['p2_advance'][0]['pass_mark'],
                    'pass': check_pass(data['p2_advance'][0]['mark_obtained'],data['p2_advance'][0]['pass_mark'])
            }],
            "p3_java":[{
                    'mark_obtained':data['p3_java'][0]['mark_obtained'],
                    'pass_mark':data['p3_java'][0]['pass_mark'],
                    'pass': check_pass(data['p3_java'][0]['mark_obtained'],data['p3_java'][0]['pass_mark'])
            }],
            "p4_java":[{
                    'mark_obtained':data['p4_java'][0]['mark_obtained'],
                    'pass_mark':data['p4_java'][0]['pass_mark'],
                    'pass': check_pass(data['p4_java'][0]['mark_obtained'],data['p4_java'][0]['pass_mark'])
            }],
            "p3_python":[{
                    'mark_obtained':data['p3_python'][0]['mark_obtained'],
                    'pass_mark':data['p3_python'][0]['pass_mark'],
                    'pass': check_pass(data['p3_python'][0]['mark_obtained'],data['p3_python'][0]['pass_mark'])
            }],
            "p4_python":[{
                    'mark_obtained':data['p4_python'][0]['mark_obtained'],
                    'pass_mark':data['p4_python'][0]['pass_mark'],
                    'pass': check_pass(data['p4_python'][0]['mark_obtained'],data['p4_python'][0]['pass_mark'])
            }],
            "p5_cloud_series":[{
                    'mark_obtained':data['p5_cloud_series'][0]['mark_obtained'],
                    'pass_mark':data['p5_cloud_series'][0]['pass_mark'],
                    'pass': check_pass(data['p5_cloud_series'][0]['mark_obtained'],data['p5_cloud_series'][0]['pass_mark'])
            }],
            "p5_full_stack":[{
                    'mark_obtained':data['p5_full_stack'][0]['mark_obtained'],
                    'pass_mark':data['p5_full_stack'][0]['pass_mark'],
                    'pass': check_pass(data['p5_full_stack'][0]['mark_obtained'],data['p5_full_stack'][0]['pass_mark'])
            }],
            "p5_data_analysis":[{
                    'mark_obtained':data['p5_data_analysis'][0]['mark_obtained'],
                    'pass_mark':data['p5_data_analysis'][0]['pass_mark'],
                    'pass': check_pass(data['p5_data_analysis'][0]['mark_obtained'],data['p5_data_analysis'][0]['pass_mark'])
            }],
            "p5_machine_learning":[{
                    'mark_obtained':data['p5_machine_learning'][0]['mark_obtained'],
                    'pass_mark':data['p5_machine_learning'][0]['pass_mark'],
                    'pass': check_pass(data['p5_machine_learning'][0]['mark_obtained'],data['p5_machine_learning'][0]['pass_mark'])
            }],
            "c2_odd":[{
                    'mark_obtained':data['c2_odd'][0]['mark_obtained'],
                    'pass_mark':data['c2_odd'][0]['pass_mark'],
                    'pass': check_pass(data['c2_odd'][0]['mark_obtained'],data['c2_odd'][0]['pass_mark'])
            }],
            "c2_even":[{
                    'mark_obtained':data['c2_even'][0]['mark_obtained'],
                    'pass_mark':data['c2_even'][0]['pass_mark'],
                    'pass': check_pass(data['c2_even'][0]['mark_obtained'],data['c2_even'][0]['pass_mark'])
            }],
            "c3_odd(III core sub)":[{
                    'mark_obtained':data['c3_odd(III core sub)'][0]['mark_obtained'],
                    'pass_mark':data['c3_odd(III core sub)'][0]['pass_mark'],
                    'pass': check_pass(data['c3_odd(III core sub)'][0]['mark_obtained'],data['c3_odd(III core sub)'][0]['pass_mark'])
            }],
            "c3_even(IV core sub)":[{
                    'mark_obtained':data['c3_even(IV core sub)'][0]['mark_obtained'],
                    'pass_mark':data['c3_even(IV core sub)'][0]['pass_mark'],
                    'pass': check_pass(data['c3_even(IV core sub)'][0]['mark_obtained'],data['c3_even(IV core sub)'][0]['pass_mark'])
            }],
            "c3_full(I to IV sub)":[{
                    'mark_obtained':data['c3_full(I to IV sub)'][0]['mark_obtained'],
                    'pass_mark':data['c3_full(I to IV sub)'][0]['pass_mark'],
                    'pass': check_pass(data['c3_full(I to IV sub)'][0]['mark_obtained'],data['c3_full(I to IV sub)'][0]['pass_mark'])
            }],
            "c4_odd(V core sub)":[{
                    'mark_obtained':data['c4_odd(V core sub)'][0]['mark_obtained'],
                    'pass_mark':data['c4_odd(V core sub)'][0]['pass_mark'],
                    'pass': check_pass(data['c4_odd(V core sub)'][0]['mark_obtained'],data['c4_odd(V core sub)'][0]['pass_mark'])
            }],
            "c4_even(VI core sub)":[{
                    'mark_obtained':data['c4_even(VI core sub)'][0]['mark_obtained'],
                    'pass_mark':data['c4_even(VI core sub)'][0]['pass_mark'],
                    'pass': check_pass(data['c4_even(VI core sub)'][0]['mark_obtained'],data['c4_even(VI core sub)'][0]['pass_mark'])
            }],
            "c4_full(I to VI sub)":[{
                    'mark_obtained':data['c4_full(I to VI sub)'][0]['mark_obtained'],
                    'pass_mark':data['c4_full(I to VI sub)'][0]['pass_mark'],
                    'pass': check_pass(data['c4_full(I to VI sub)'][0]['mark_obtained'],data['c4_full(I to VI sub)'][0]['pass_mark'])
            }],
            "c5_odd(VII core sub)":[{
                    'mark_obtained':data['c5_odd(VII core sub)'][0]['mark_obtained'],
                    'pass_mark':data['c5_odd(VII core sub)'][0]['pass_mark'],
                    'pass': check_pass(data['c5_odd(VII core sub)'][0]['mark_obtained'],data['c5_odd(VII core sub)'][0]['pass_mark'])
            }],
            "c5_even(VIII core sub)":[{
                    'mark_obtained':data['c5_even(VIII core sub)'][0]['mark_obtained'],
                    'pass_mark':data['c5_even(VIII core sub)'][0]['pass_mark'],
                    'pass': check_pass(data['c5_even(VIII core sub)'][0]['mark_obtained'],data['c5_even(VIII core sub)'][0]['pass_mark'])
            }],
            "c5_full(I to VIII core sub)":[{
                    'mark_obtained':data['c5_full(I to VIII core sub)'][0]['mark_obtained'],
                    'pass_mark':data['c5_full(I to VIII core sub)'][0]['pass_mark'],
                    'pass': check_pass(data['c5_full(I to VIII core sub)'][0]['mark_obtained'],data['c5_full(I to VIII core sub)'][0]['pass_mark'])
            }],
            "a1":[{
                    'mark_obtained':data['a1'][0]['mark_obtained'],
                    'pass_mark':data['a1'][0]['pass_mark'],
                    'pass': check_pass(data['a1'][0]['mark_obtained'],data['a1'][0]['pass_mark'])
            }],
            "a2":[{
                    'mark_obtained':data['a2'][0]['mark_obtained'],
                    'pass_mark':data['a2'][0]['pass_mark'],
                    'pass': check_pass(data['a2'][0]['mark_obtained'],data['a2'][0]['pass_mark'])
            }],
            "a3":[{
                    'mark_obtained':data['a3'][0]['mark_obtained'],
                    'pass_mark':data['a3'][0]['pass_mark'],
                    'pass': check_pass(data['a3'][0]['mark_obtained'],data['a3'][0]['pass_mark'])
            }],
            "s1":[{
                    'mark_obtained':data['s1'][0]['mark_obtained'],
                    'pass_mark':data['s1'][0]['pass_mark'],
                    'pass': check_pass(data['s1'][0]['mark_obtained'],data['s1'][0]['pass_mark'])
            }],
            "s2":[{
                    'mark_obtained':data['s2'][0]['mark_obtained'],
                    'pass_mark':data['s2'][0]['pass_mark'],
                    'pass': check_pass(data['s2'][0]['mark_obtained'],data['s2'][0]['pass_mark'])
            }],
            "s3":[{
                    'mark_obtained':data['s3'][0]['mark_obtained'],
                    'pass_mark':data['s3'][0]['pass_mark'],
                    'pass': check_pass(data['s3'][0]['mark_obtained'],data['s3'][0]['pass_mark'])
            }],
            "e3(1st sem)":[{
                    'mark_obtained':data['e3(1st sem)'][0]['mark_obtained'],
                    'pass_mark':data['e3(1st sem)'][0]['pass_mark'],
                    'pass': check_pass(data['e3(1st sem)'][0]['mark_obtained'],data['e3(1st sem)'][0]['pass_mark'])
            }],
            "e3(2nd sem)":[{
                    'mark_obtained':data['e3(2nd sem)'][0]['mark_obtained'],
                    'pass_mark':data['e3(2nd sem)'][0]['pass_mark'],
                    'pass': check_pass(data['e3(2nd sem)'][0]['mark_obtained'],data['e3(2nd sem)'][0]['pass_mark'])
            }],
            "e3(consolidate)":[{
                    'mark_obtained':data['e3(consolidate)'][0]['mark_obtained'],
                    'pass_mark':data['e3(consolidate)'][0]['pass_mark'],
                    'pass': check_pass(data['e3(consolidate)'][0]['mark_obtained'],data['e3(consolidate)'][0]['pass_mark'])
            }]
        }
        res = st_db[collection_name].insert_one(student)
        print(res)
        if res:
            return {"success":"Entered new User"},200
        else:
            return {"message":"Failed to write in db"}

    def put(self,branch,year,usn):
        data = request.get_json()
        st_db = client[branch]
        collection_name = year
        students = st_db[collection_name].find()
        student = next(filter(lambda x: x['usn']==usn,students),None)
        if student is None:
            student = {
                "name":data['name'],
                "mail_id":data['mail_id'],
                "usn":usn,
                "phone_no":data['phone_no'],
                "branch":data['branch'],
                "vtu_result":data['vtu_result'],
                "year":year,
                "p1_basics":[{
                    'mark_obtained':data['p1_basics'][0]['mark_obtained'],
                    'pass_mark':data['p1_basics'][0]['pass_mark'],
                    'pass': check_pass(data['p1_basics'][0]['mark_obtained'],data['p1_basics'][0]['pass_mark'])
                }],
                "p2_c":[{
                        'mark_obtained':data['p2_c'][0]['mark_obtained'],
                        'pass_mark':data['p2_c'][0]['pass_mark'],
                        'pass': check_pass(data['p2_c'][0]['mark_obtained'],data['p2_c'][0]['pass_mark'])
                }],
                "p2_python":[{
                        'mark_obtained':data['p2_python'][0]['mark_obtained'],
                        'pass_mark':data['p2_python'][0]['pass_mark'],
                        'pass': check_pass(data['p2_python'][0]['mark_obtained'],data['p2_python'][0]['pass_mark'])
                }],
                "p2_advance":[{
                        'mark_obtained':data['p2_advance'][0]['mark_obtained'],
                        'pass_mark':data['p2_advance'][0]['pass_mark'],
                        'pass': check_pass(data['p2_advance'][0]['mark_obtained'],data['p2_advance'][0]['pass_mark'])
                }],
                "p3_java":[{
                        'mark_obtained':data['p3_java'][0]['mark_obtained'],
                        'pass_mark':data['p3_java'][0]['pass_mark'],
                        'pass': check_pass(data['p3_java'][0]['mark_obtained'],data['p3_java'][0]['pass_mark'])
                }],
                "p4_java":[{
                        'mark_obtained':data['p4_java'][0]['mark_obtained'],
                        'pass_mark':data['p4_java'][0]['pass_mark'],
                        'pass': check_pass(data['p4_java'][0]['mark_obtained'],data['p4_java'][0]['pass_mark'])
                }],
                "p3_python":[{
                        'mark_obtained':data['p3_python'][0]['mark_obtained'],
                        'pass_mark':data['p3_python'][0]['pass_mark'],
                        'pass': check_pass(data['p3_python'][0]['mark_obtained'],data['p3_python'][0]['pass_mark'])
                }],
                "p4_python":[{
                        'mark_obtained':data['p4_python'][0]['mark_obtained'],
                        'pass_mark':data['p4_python'][0]['pass_mark'],
                        'pass': check_pass(data['p4_python'][0]['mark_obtained'],data['p4_python'][0]['pass_mark'])
                }],
                "p5_cloud_series":[{
                        'mark_obtained':data['p5_cloud_series'][0]['mark_obtained'],
                        'pass_mark':data['p5_cloud_series'][0]['pass_mark'],
                        'pass': check_pass(data['p5_cloud_series'][0]['mark_obtained'],data['p5_cloud_series'][0]['pass_mark'])
                }],
                "p5_full_stack":[{
                        'mark_obtained':data['p5_full_stack'][0]['mark_obtained'],
                        'pass_mark':data['p5_full_stack'][0]['pass_mark'],
                        'pass': check_pass(data['p5_full_stack'][0]['mark_obtained'],data['p5_full_stack'][0]['pass_mark'])
                }],
                "p5_data_analysis":[{
                        'mark_obtained':data['p5_data_analysis'][0]['mark_obtained'],
                        'pass_mark':data['p5_data_analysis'][0]['pass_mark'],
                        'pass': check_pass(data['p5_data_analysis'][0]['mark_obtained'],data['p5_data_analysis'][0]['pass_mark'])
                }],
                "p5_machine_learning":[{
                        'mark_obtained':data['p5_machine_learning'][0]['mark_obtained'],
                        'pass_mark':data['p5_machine_learning'][0]['pass_mark'],
                        'pass': check_pass(data['p5_machine_learning'][0]['mark_obtained'],data['p5_machine_learning'][0]['pass_mark'])
                }],
                "c2_odd":[{
                        'mark_obtained':data['c2_odd'][0]['mark_obtained'],
                        'pass_mark':data['c2_odd'][0]['pass_mark'],
                        'pass': check_pass(data['c2_odd'][0]['mark_obtained'],data['c2_odd'][0]['pass_mark'])
                }],
                "c2_even":[{
                        'mark_obtained':data['c2_even'][0]['mark_obtained'],
                        'pass_mark':data['c2_even'][0]['pass_mark'],
                        'pass': check_pass(data['c2_even'][0]['mark_obtained'],data['c2_even'][0]['pass_mark'])
                }],
                "c3_odd(III core sub)":[{
                        'mark_obtained':data['c3_odd(III core sub)'][0]['mark_obtained'],
                        'pass_mark':data['c3_odd(III core sub)'][0]['pass_mark'],
                        'pass': check_pass(data['c3_odd(III core sub)'][0]['mark_obtained'],data['c3_odd(III core sub)'][0]['pass_mark'])
                }],
                "c3_even(IV core sub)":[{
                        'mark_obtained':data['c3_even(IV core sub)'][0]['mark_obtained'],
                        'pass_mark':data['c3_even(IV core sub)'][0]['pass_mark'],
                        'pass': check_pass(data['c3_even(IV core sub)'][0]['mark_obtained'],data['c3_even(IV core sub)'][0]['pass_mark'])
                }],
                "c3_full(I to IV sub)":[{
                        'mark_obtained':data['c3_full(I to IV sub)'][0]['mark_obtained'],
                        'pass_mark':data['c3_full(I to IV sub)'][0]['pass_mark'],
                        'pass': check_pass(data['c3_full(I to IV sub)'][0]['mark_obtained'],data['c3_full(I to IV sub)'][0]['pass_mark'])
                }],
                "c4_odd(V core sub)":[{
                        'mark_obtained':data['c4_odd(V core sub)'][0]['mark_obtained'],
                        'pass_mark':data['c4_odd(V core sub)'][0]['pass_mark'],
                        'pass': check_pass(data['c4_odd(V core sub)'][0]['mark_obtained'],data['c4_odd(V core sub)'][0]['pass_mark'])
                }],
                "c4_even(VI core sub)":[{
                        'mark_obtained':data['c4_even(VI core sub)'][0]['mark_obtained'],
                        'pass_mark':data['c4_even(VI core sub)'][0]['pass_mark'],
                        'pass': check_pass(data['c4_even(VI core sub)'][0]['mark_obtained'],data['c4_even(VI core sub)'][0]['pass_mark'])
                }],
                "c4_full(I to VI sub)":[{
                        'mark_obtained':data['c4_full(I to VI sub)'][0]['mark_obtained'],
                        'pass_mark':data['c4_full(I to VI sub)'][0]['pass_mark'],
                        'pass': check_pass(data['c4_full(I to VI sub)'][0]['mark_obtained'],data['c4_full(I to VI sub)'][0]['pass_mark'])
                }],
                "c5_odd(VII core sub)":[{
                        'mark_obtained':data['c5_odd(VII core sub)'][0]['mark_obtained'],
                        'pass_mark':data['c5_odd(VII core sub)'][0]['pass_mark'],
                        'pass': check_pass(data['c5_odd(VII core sub)'][0]['mark_obtained'],data['c5_odd(VII core sub)'][0]['pass_mark'])
                }],
                "c5_even(VIII core sub)":[{
                        'mark_obtained':data['c5_even(VIII core sub)'][0]['mark_obtained'],
                        'pass_mark':data['c5_even(VIII core sub)'][0]['pass_mark'],
                        'pass': check_pass(data['c5_even(VIII core sub)'][0]['mark_obtained'],data['c5_even(VIII core sub)'][0]['pass_mark'])
                }],
                "c5_full(I to VIII core sub)":[{
                        'mark_obtained':data['c5_full(I to VIII core sub)'][0]['mark_obtained'],
                        'pass_mark':data['c5_full(I to VIII core sub)'][0]['pass_mark'],
                        'pass': check_pass(data['c5_full(I to VIII core sub)'][0]['mark_obtained'],data['c5_full(I to VIII core sub)'][0]['pass_mark'])
                }],
                "a1":[{
                        'mark_obtained':data['a1'][0]['mark_obtained'],
                        'pass_mark':data['a1'][0]['pass_mark'],
                        'pass': check_pass(data['a1'][0]['mark_obtained'],data['a1'][0]['pass_mark'])
                }],
                "a2":[{
                        'mark_obtained':data['a2'][0]['mark_obtained'],
                        'pass_mark':data['a2'][0]['pass_mark'],
                        'pass': check_pass(data['a2'][0]['mark_obtained'],data['a2'][0]['pass_mark'])
                }],
                "a3":[{
                        'mark_obtained':data['a3'][0]['mark_obtained'],
                        'pass_mark':data['a3'][0]['pass_mark'],
                        'pass': check_pass(data['a3'][0]['mark_obtained'],data['a3'][0]['pass_mark'])
                }],
                "s1":[{
                        'mark_obtained':data['s1'][0]['mark_obtained'],
                        'pass_mark':data['s1'][0]['pass_mark'],
                        'pass': check_pass(data['s1'][0]['mark_obtained'],data['s1'][0]['pass_mark'])
                }],
                "s2":[{
                        'mark_obtained':data['s2'][0]['mark_obtained'],
                        'pass_mark':data['s2'][0]['pass_mark'],
                        'pass': check_pass(data['s2'][0]['mark_obtained'],data['s2'][0]['pass_mark'])
                }],
                "s3":[{
                        'mark_obtained':data['s3'][0]['mark_obtained'],
                        'pass_mark':data['s3'][0]['pass_mark'],
                        'pass': check_pass(data['s3'][0]['mark_obtained'],data['s3'][0]['pass_mark'])
                }],
                "e3(1st sem)":[{
                        'mark_obtained':data['e3(1st sem)'][0]['mark_obtained'],
                        'pass_mark':data['e3(1st sem)'][0]['pass_mark'],
                        'pass': check_pass(data['e3(1st sem)'][0]['mark_obtained'],data['e3(1st sem)'][0]['pass_mark'])
                }],
                "e3(2nd sem)":[{
                        'mark_obtained':data['e3(2nd sem)'][0]['mark_obtained'],
                        'pass_mark':data['e3(2nd sem)'][0]['pass_mark'],
                        'pass': check_pass(data['e3(2nd sem)'][0]['mark_obtained'],data['e3(2nd sem)'][0]['pass_mark'])
                }],
                "e3(consolidate)":[{
                        'mark_obtained':data['e3(consolidate)'][0]['mark_obtained'],
                        'pass_mark':data['e3(consolidate)'][0]['pass_mark'],
                        'pass': check_pass(data['e3(consolidate)'][0]['mark_obtained'],data['e3(consolidate)'][0]['pass_mark'])
                }]
            }
            res = st_db[collection_name].insert_one(student)
            if res:
                return {"message":"Inserted sucessfully"}, 200
            else:
                return {"message":"Error while inserting"}, 400
        else:
            st_db[collection_name].update(
                { 
                    "usn": usn 
                },
                {
                        "name":data['name'],
                        "mail_id":data['mail_id'],
                        "usn":usn,
                        "phone_no":data['phone_no'],
                        "branch":data['branch'],
                        "vtu_result":data['vtu_result'],
                        "year":year,
                        "p1_basics":[{
                                'mark_obtained':data['p1_basics'][0]['mark_obtained'],
                                'pass_mark':data['p1_basics'][0]['pass_mark'],
                                'pass': check_pass(data['p1_basics'][0]['mark_obtained'],data['p1_basics'][0]['pass_mark'])
                        }],
                        "p2_c":[{
                                'mark_obtained':data['p2_c'][0]['mark_obtained'],
                                'pass_mark':data['p2_c'][0]['pass_mark'],
                                'pass': check_pass(data['p2_c'][0]['mark_obtained'],data['p2_c'][0]['pass_mark'])
                        }],
                        "p2_python":[{
                                'mark_obtained':data['p2_python'][0]['mark_obtained'],
                                'pass_mark':data['p2_python'][0]['pass_mark'],
                                'pass': check_pass(data['p2_python'][0]['mark_obtained'],data['p2_python'][0]['pass_mark'])
                        }],
                        "p2_advance":[{
                                'mark_obtained':data['p2_advance'][0]['mark_obtained'],
                                'pass_mark':data['p2_advance'][0]['pass_mark'],
                                'pass': check_pass(data['p2_advance'][0]['mark_obtained'],data['p2_advance'][0]['pass_mark'])
                        }],
                        "p3_java":[{
                                'mark_obtained':data['p3_java'][0]['mark_obtained'],
                                'pass_mark':data['p3_java'][0]['pass_mark'],
                                'pass': check_pass(data['p3_java'][0]['mark_obtained'],data['p3_java'][0]['pass_mark'])
                        }],
                        "p4_java":[{
                                'mark_obtained':data['p4_java'][0]['mark_obtained'],
                                'pass_mark':data['p4_java'][0]['pass_mark'],
                                'pass': check_pass(data['p4_java'][0]['mark_obtained'],data['p4_java'][0]['pass_mark'])
                        }],
                        "p3_python":[{
                                'mark_obtained':data['p3_python'][0]['mark_obtained'],
                                'pass_mark':data['p3_python'][0]['pass_mark'],
                                'pass': check_pass(data['p3_python'][0]['mark_obtained'],data['p3_python'][0]['pass_mark'])
                        }],
                        "p4_python":[{
                                'mark_obtained':data['p4_python'][0]['mark_obtained'],
                                'pass_mark':data['p4_python'][0]['pass_mark'],
                                'pass': check_pass(data['p4_python'][0]['mark_obtained'],data['p4_python'][0]['pass_mark'])
                        }],
                        "p5_cloud_series":[{
                                'mark_obtained':data['p5_cloud_series'][0]['mark_obtained'],
                                'pass_mark':data['p5_cloud_series'][0]['pass_mark'],
                                'pass': check_pass(data['p5_cloud_series'][0]['mark_obtained'],data['p5_cloud_series'][0]['pass_mark'])
                        }],
                        "p5_full_stack":[{
                                'mark_obtained':data['p5_full_stack'][0]['mark_obtained'],
                                'pass_mark':data['p5_full_stack'][0]['pass_mark'],
                                'pass': check_pass(data['p5_full_stack'][0]['mark_obtained'],data['p5_full_stack'][0]['pass_mark'])
                        }],
                        "p5_data_analysis":[{
                                'mark_obtained':data['p5_data_analysis'][0]['mark_obtained'],
                                'pass_mark':data['p5_data_analysis'][0]['pass_mark'],
                                'pass': check_pass(data['p5_data_analysis'][0]['mark_obtained'],data['p5_data_analysis'][0]['pass_mark'])
                        }],
                        "p5_machine_learning":[{
                                'mark_obtained':data['p5_machine_learning'][0]['mark_obtained'],
                                'pass_mark':data['p5_machine_learning'][0]['pass_mark'],
                                'pass': check_pass(data['p5_machine_learning'][0]['mark_obtained'],data['p5_machine_learning'][0]['pass_mark'])
                        }],
                        "c2_odd":[{
                                'mark_obtained':data['c2_odd'][0]['mark_obtained'],
                                'pass_mark':data['c2_odd'][0]['pass_mark'],
                                'pass': check_pass(data['c2_odd'][0]['mark_obtained'],data['c2_odd'][0]['pass_mark'])
                        }],
                        "c2_even":[{
                                'mark_obtained':data['c2_even'][0]['mark_obtained'],
                                'pass_mark':data['c2_even'][0]['pass_mark'],
                                'pass': check_pass(data['c2_even'][0]['mark_obtained'],data['c2_even'][0]['pass_mark'])
                        }],
                        "c3_odd(III core sub)":[{
                                'mark_obtained':data['c3_odd(III core sub)'][0]['mark_obtained'],
                                'pass_mark':data['c3_odd(III core sub)'][0]['pass_mark'],
                                'pass': check_pass(data['c3_odd(III core sub)'][0]['mark_obtained'],data['c3_odd(III core sub)'][0]['pass_mark'])
                        }],
                        "c3_even(IV core sub)":[{
                                'mark_obtained':data['c3_even(IV core sub)'][0]['mark_obtained'],
                                'pass_mark':data['c3_even(IV core sub)'][0]['pass_mark'],
                                'pass': check_pass(data['c3_even(IV core sub)'][0]['mark_obtained'],data['c3_even(IV core sub)'][0]['pass_mark'])
                        }],
                        "c3_full(I to IV sub)":[{
                                'mark_obtained':data['c3_full(I to IV sub)'][0]['mark_obtained'],
                                'pass_mark':data['c3_full(I to IV sub)'][0]['pass_mark'],
                                'pass': check_pass(data['c3_full(I to IV sub)'][0]['mark_obtained'],data['c3_full(I to IV sub)'][0]['pass_mark'])
                        }],
                        "c4_odd(V core sub)":[{
                                'mark_obtained':data['c4_odd(V core sub)'][0]['mark_obtained'],
                                'pass_mark':data['c4_odd(V core sub)'][0]['pass_mark'],
                                'pass': check_pass(data['c4_odd(V core sub)'][0]['mark_obtained'],data['c4_odd(V core sub)'][0]['pass_mark'])
                        }],
                        "c4_even(VI core sub)":[{
                                'mark_obtained':data['c4_even(VI core sub)'][0]['mark_obtained'],
                                'pass_mark':data['c4_even(VI core sub)'][0]['pass_mark'],
                                'pass': check_pass(data['c4_even(VI core sub)'][0]['mark_obtained'],data['c4_even(VI core sub)'][0]['pass_mark'])
                        }],
                        "c4_full(I to VI sub)":[{
                                'mark_obtained':data['c4_full(I to VI sub)'][0]['mark_obtained'],
                                'pass_mark':data['c4_full(I to VI sub)'][0]['pass_mark'],
                                'pass': check_pass(data['c4_full(I to VI sub)'][0]['mark_obtained'],data['c4_full(I to VI sub)'][0]['pass_mark'])
                        }],
                        "c5_odd(VII core sub)":[{
                                'mark_obtained':data['c5_odd(VII core sub)'][0]['mark_obtained'],
                                'pass_mark':data['c5_odd(VII core sub)'][0]['pass_mark'],
                                'pass': check_pass(data['c5_odd(VII core sub)'][0]['mark_obtained'],data['c5_odd(VII core sub)'][0]['pass_mark'])
                        }],
                        "c5_even(VIII core sub)":[{
                                'mark_obtained':data['c5_even(VIII core sub)'][0]['mark_obtained'],
                                'pass_mark':data['c5_even(VIII core sub)'][0]['pass_mark'],
                                'pass': check_pass(data['c5_even(VIII core sub)'][0]['mark_obtained'],data['c5_even(VIII core sub)'][0]['pass_mark'])
                        }],
                        "c5_full(I to VIII core sub)":[{
                                'mark_obtained':data['c5_full(I to VIII core sub)'][0]['mark_obtained'],
                                'pass_mark':data['c5_full(I to VIII core sub)'][0]['pass_mark'],
                                'pass': check_pass(data['c5_full(I to VIII core sub)'][0]['mark_obtained'],data['c5_full(I to VIII core sub)'][0]['pass_mark'])
                        }],
                        "a1":[{
                                'mark_obtained':data['a1'][0]['mark_obtained'],
                                'pass_mark':data['a1'][0]['pass_mark'],
                                'pass': check_pass(data['a1'][0]['mark_obtained'],data['a1'][0]['pass_mark'])
                        }],
                        "a2":[{
                                'mark_obtained':data['a2'][0]['mark_obtained'],
                                'pass_mark':data['a2'][0]['pass_mark'],
                                'pass': check_pass(data['a2'][0]['mark_obtained'],data['a2'][0]['pass_mark'])
                        }],
                        "a3":[{
                                'mark_obtained':data['a3'][0]['mark_obtained'],
                                'pass_mark':data['a3'][0]['pass_mark'],
                                'pass': check_pass(data['a3'][0]['mark_obtained'],data['a3'][0]['pass_mark'])
                        }],
                        "s1":[{
                                'mark_obtained':data['s1'][0]['mark_obtained'],
                                'pass_mark':data['s1'][0]['pass_mark'],
                                'pass': check_pass(data['s1'][0]['mark_obtained'],data['s1'][0]['pass_mark'])
                        }],
                        "s2":[{
                                'mark_obtained':data['s2'][0]['mark_obtained'],
                                'pass_mark':data['s2'][0]['pass_mark'],
                                'pass': check_pass(data['s2'][0]['mark_obtained'],data['s2'][0]['pass_mark'])
                        }],
                        "s3":[{
                                'mark_obtained':data['s3'][0]['mark_obtained'],
                                'pass_mark':data['s3'][0]['pass_mark'],
                                'pass': check_pass(data['s3'][0]['mark_obtained'],data['s3'][0]['pass_mark'])
                        }],
                        "e3(1st sem)":[{
                                'mark_obtained':data['e3(1st sem)'][0]['mark_obtained'],
                                'pass_mark':data['e3(1st sem)'][0]['pass_mark'],
                                'pass': check_pass(data['e3(1st sem)'][0]['mark_obtained'],data['e3(1st sem)'][0]['pass_mark'])
                        }],
                        "e3(2nd sem)":[{
                                'mark_obtained':data['e3(2nd sem)'][0]['mark_obtained'],
                                'pass_mark':data['e3(2nd sem)'][0]['pass_mark'],
                                'pass': check_pass(data['e3(2nd sem)'][0]['mark_obtained'],data['e3(2nd sem)'][0]['pass_mark'])
                        }],
                        "e3(consolidate)":[{
                                'mark_obtained':data['e3(consolidate)'][0]['mark_obtained'],
                                'pass_mark':data['e3(consolidate)'][0]['pass_mark'],
                                'pass': check_pass(data['e3(consolidate)'][0]['mark_obtained'],data['e3(consolidate)'][0]['pass_mark'])
                        }]
                },
            )
            return {"message":"updated"},200

    def get(self,branch,year):
        st_db = client[branch]
        collection_name = year
        students = []
        results = st_db[collection_name].find()
        for data in results:
            students.append({
                    "name":data['name'],
                    "mail_id":data['mail_id'],
                    "usn":data['usn'],
                    "phone_no":data['phone_no'],
                    "branch":data['branch'],
                    "vtu_result":data["vtu_result"],
                    "year":data['year'],
                    "marks":[
                        {
                                "programming(Px)":[
                                        {
                                        "p1_basics":{
                                                'mark_obtained':data['p1_basics'][0]['mark_obtained'],
                                                'pass_mark':data['p1_basics'][0]['pass_mark'],
                                                'pass': data['p1_basics'][0]['pass']
                                                }
                                        },
                                        {
                                        "p2_c":{
                                                'mark_obtained':data['p2_c'][0]['mark_obtained'],
                                                'pass_mark':data['p2_c'][0]['pass_mark'],
                                                'pass': data['p2_c'][0]['pass']
                                        }       },
                                        {
                                        "p2_python":{
                                                'mark_obtained':data['p2_python'][0]['mark_obtained'],
                                                'pass_mark':data['p2_python'][0]['pass_mark'],
                                                'pass': data['p2_python'][0]['pass']
                                                }
                                        },
                                        {
                                        "p2_advance":{
                                                'mark_obtained':data['p2_advance'][0]['mark_obtained'],
                                                'pass_mark':data['p2_advance'][0]['pass_mark'],
                                                'pass': data['p2_advance'][0]['pass']
                                                }
                                        },
                                        {
                                        "p3_java":{
                                                'mark_obtained':data['p3_java'][0]['mark_obtained'],
                                                'pass_mark':data['p3_java'][0]['pass_mark'],
                                                'pass': data['p3_java'][0]['pass']
                                                }
                                        },
                                        {
                                        "p4_java":{
                                                'mark_obtained':data['p4_java'][0]['mark_obtained'],
                                                'pass_mark':data['p4_java'][0]['pass_mark'],
                                                'pass': data['p4_java'][0]['pass']
                                                }
                                        },
                                        {
                                        "p3_python":{
                                                'mark_obtained':data['p3_python'][0]['mark_obtained'],
                                                'pass_mark':data['p3_python'][0]['pass_mark'],
                                                'pass': data['p3_python'][0]['pass']
                                                }
                                        },
                                        {
                                        "p4_python":{
                                                'mark_obtained':data['p4_python'][0]['mark_obtained'],
                                                'pass_mark':data['p4_python'][0]['pass_mark'],
                                                'pass': data['p4_python'][0]['pass']
                                                }
                                        },
                                        {
                                        "p5_cloud_series":{
                                                'mark_obtained':data['p5_cloud_series'][0]['mark_obtained'],
                                                'pass_mark':data['p5_cloud_series'][0]['pass_mark'],
                                                'pass': data['p5_cloud_series'][0]['pass']
                                                }
                                        },
                                        {
                                        "p5_full_stack":{
                                                'mark_obtained':data['p5_full_stack'][0]['mark_obtained'],
                                                'pass_mark':data['p5_full_stack'][0]['pass_mark'],
                                                'pass': data['p5_full_stack'][0]['pass']
                                                }
                                        },
                                        {
                                        "p5_data_analysis":{
                                                'mark_obtained':data['p5_data_analysis'][0]['mark_obtained'],
                                                'pass_mark':data['p5_data_analysis'][0]['pass_mark'],
                                                'pass': data['p5_data_analysis'][0]['pass']
                                                }
                                        },
                                        {
                                        "p5_machine_learning":{
                                                'mark_obtained':data['p5_machine_learning'][0]['mark_obtained'],
                                                'pass_mark':data['p5_machine_learning'][0]['pass_mark'],
                                                'pass': data['p5_machine_learning'][0]['pass']
                                                }
                                        },
                                ],
                                "core(Cx)":[
                                        {
                                        "c2_odd":{
                                                'mark_obtained':data['c2_odd'][0]['mark_obtained'],
                                                'pass_mark':data['c2_odd'][0]['pass_mark'],
                                                'pass': data['c2_odd'][0]['pass']
                                                }
                                        },
                                        {
                                        "c2_even":{
                                                'mark_obtained':data['c2_even'][0]['mark_obtained'],
                                                'pass_mark':data['c2_even'][0]['pass_mark'],
                                                'pass': data['c2_even'][0]['pass']
                                                }
                                        },
                                        {
                                        "c3_odd(III core sub)":{
                                                'mark_obtained':data['c3_odd(III core sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c3_odd(III core sub)'][0]['pass_mark'],
                                                'pass': data['c3_odd(III core sub)'][0]['pass']
                                                }
                                        },
                                        {
                                        "c3_even(IV core sub)":{
                                                'mark_obtained':data['c3_even(IV core sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c3_even(IV core sub)'][0]['pass_mark'],
                                                'pass': data['c3_even(IV core sub)'][0]['pass']
                                                }
                                        },
                                        {
                                        "c3_full(I to IV sub)":{
                                                'mark_obtained':data['c3_full(I to IV sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c3_full(I to IV sub)'][0]['pass_mark'],
                                                'pass': data['c3_full(I to IV sub)'][0]['pass']
                                                }
                                        },
                                        {
                                        "c4_odd(V core sub)":{
                                                'mark_obtained':data['c4_odd(V core sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c4_odd(V core sub)'][0]['pass_mark'],
                                                'pass': data['c4_odd(V core sub)'][0]['pass']
                                                }
                                        },
                                        {
                                        "c4_even(VI core sub)":{
                                                'mark_obtained':data['c4_even(VI core sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c4_even(VI core sub)'][0]['pass_mark'],
                                                'pass': data['c4_even(VI core sub)'][0]['pass']
                                                }
                                        },
                                        {
                                        "c4_full(I to VI sub)":{
                                                'mark_obtained':data['c4_full(I to VI sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c4_full(I to VI sub)'][0]['pass_mark'],
                                                'pass': data['c4_full(I to VI sub)'][0]['pass']
                                                }       
                                        },
                                        {
                                        "c5_odd(VII core sub)":{
                                                'mark_obtained':data['c5_odd(VII core sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c5_odd(VII core sub)'][0]['pass_mark'],
                                                'pass': data['c5_odd(VII core sub)'][0]['pass']
                                                }
                                        },
                                        {
                                        "c5_even(VIII core sub)":{
                                                'mark_obtained':data['c5_even(VIII core sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c5_even(VIII core sub)'][0]['pass_mark'],
                                                'pass': data['c5_even(VIII core sub)'][0]['pass']
                                                }
                                        },
                                        {
                                        "c5_full(I to VIII core sub)":{
                                                'mark_obtained':data['c5_full(I to VIII core sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c5_full(I to VIII core sub)'][0]['pass_mark'],
                                                'pass': data['c5_full(I to VIII core sub)'][0]['pass']
                                                }
                                        },
                                ],
                                "aptitude(Ax)":[
                                        {
                                        "a1":{
                                                'mark_obtained':data['a1'][0]['mark_obtained'],
                                                'pass_mark':data['a1'][0]['pass_mark'],
                                                'pass': data['a1'][0]['pass']
                                                }
                                        },
                                        {
                                        "a2":{
                                                'mark_obtained':data['a2'][0]['mark_obtained'],
                                                'pass_mark':data['a2'][0]['pass_mark'],
                                                'pass': data['a2'][0]['pass']
                                                }
                                        },
                                        {
                                        "a3":{
                                                'mark_obtained':data['a3'][0]['mark_obtained'],
                                                'pass_mark':data['a3'][0]['pass_mark'],
                                                'pass': data['a3'][0]['pass']
                                                }
                                        },
                                ],
                                "soft_skill(Sx)":[
                                        {
                                        "s1":{
                                                'mark_obtained':data['s1'][0]['mark_obtained'],
                                                'pass_mark':data['s1'][0]['pass_mark'],
                                                'pass': data['s1'][0]['pass']
                                                }
                                        },
                                        {
                                        "s2":{
                                                'mark_obtained':data['s2'][0]['mark_obtained'],
                                                'pass_mark':data['s2'][0]['pass_mark'],
                                                'pass': data['s2'][0]['pass']
                                                }
                                        },
                                        {
                                        "s3":{
                                                'mark_obtained':data['s3'][0]['mark_obtained'],
                                                'pass_mark':data['s3'][0]['pass_mark'],
                                                'pass': data['s3'][0]['pass']
                                                }
                                        },
                                ],
                                "english(Ex)":[
                                        {
                                        "e3(1st sem)":{
                                                'mark_obtained':data['e3(1st sem)'][0]['mark_obtained'],
                                                'pass_mark':data['e3(1st sem)'][0]['pass_mark'],
                                                'pass': data['e3(1st sem)'][0]['pass']
                                                }
                                        },
                                        {
                                        "e3(2nd sem)":{
                                                'mark_obtained':data['e3(2nd sem)'][0]['mark_obtained'],
                                                'pass_mark':data['e3(2nd sem)'][0]['pass_mark'],
                                                'pass': data['e3(2nd sem)'][0]['pass']
                                                }
                                        },
                                        {
                                        "e3(consolidate)":{
                                                'mark_obtained':data['e3(consolidate)'][0]['mark_obtained'],
                                                'pass_mark':data['e3(consolidate)'][0]['pass_mark'],
                                                'pass': data['e3(consolidate)'][0]['pass']
                                                }
                                        },
                                ]
                        }
                        ],
                        "level":{
                                "PX_level":check_px_level(data),
                                "CX_level":check_cx_level(data),
                                "AX_level":check_ax_level(data),
                                "SX_level":check_sx_level(data),
                                "EX_level":check_ex_level(data)
                        }
                })
        if len(students) == 0:
            return {"message":"no datas found"}, 404
        return students, 200

def check_pass(marks_obtained,pass_mark):
        if (not(bool(marks_obtained))):
                return None
        elif (marks_obtained>=pass_mark):
                return 1
        elif (marks_obtained<pass_mark):
                return 0

def check_px_level(data):
        level = None
        if data['p1_basics'][0]['pass']==1:
                level = 'P1 Basics'
        if data['p2_c'][0]['pass']==1:
                level = 'P2 C'
        if data['p2_python'][0]['pass']==1:
                level = 'P2 Python'
        if data['p2_advance'][0]['pass']==1:
                level = 'P2 Advance'
        if data['p3_java'][0]['pass']==1:
                level = 'p3 Java'
        if data['p4_java'][0]['pass']==1:
                level = 'P4 Java'
        if data['p3_python'][0]['pass']==1:
                level = 'P3 Python'
        if data['p4_python'][0]['pass']==1:
                level = 'P4 Python'
        if data['p5_cloud_series'][0]['pass']==1:
                level = 'P5 Cloud series'
        if data['p5_full_stack'][0]['pass']==1:
                level = 'P5 Fullstack'
        if data['p5_data_analysis'][0]['pass']==1:
                level = 'P5 Data analysis'
        if data['p5_machine_learning'][0]['pass']==1:
                level = 'P5 Machine learning'
        return level

def check_cx_level(data):
        level=None
        if data['c2_odd'][0]['pass']==1:
                level = 'C2 odd'
        if data['c2_even'][0]['pass']==1:
                level = 'C2 even'
        if data['c3_odd(III core sub)'][0]['pass']==1:
                level = 'C3 odd (III core sub)'
        if data['c3_even(IV core sub)'][0]['pass']==1:
                level = 'C3 even (IV core sub)'
        if data['c3_full(I to IV sub)'][0]['pass']==1:
                level = 'C3 full (I to IV sub)'
        if data['c4_odd(V core sub)'][0]['pass']==1:
                level = 'C4 odd (V core sub)'
        if data['c4_even(VI core sub)'][0]['pass']==1:
                level = 'C4 even (VI core sub)'
        if data['c4_full(I to VI sub)'][0]['pass']==1:
                level = 'C4 full (I to VI sub)'
        if data['c5_odd(VII core sub)'][0]['pass']==1:
                level = 'C5 odd (VII core sub)'
        if data['c5_even(VIII core sub)'][0]['pass']==1:
                level = 'C5 even (VIII core sub)'
        if data['c5_full(I to VIII core sub)'][0]['pass']==1:
                level = 'C5 full (I to VIII core sub)'
        return level

def check_ax_level(data):
        level = None
        if data['a1'][0]['pass']==1:
                level = 'A1'
        if data['a2'][0]['pass']==1:
                level = 'A2'
        if data['a3'][0]['pass']==1:
                level = 'A3'
        return level

def check_sx_level(data):
        level= None
        if data['s1'][0]['pass']==1:
                level = 'S1'
        if data['s2'][0]['pass']==1:
                level = 'S2'
        if data['s3'][0]['pass']==1:
                level = 'S3'
        return level

def check_ex_level(data):
        level =None
        if data['e3(1st sem)'][0]['pass']==1:
                level = 'E3 1st sem'
        if data['e3(2nd sem)'][0]['pass']==1:
                level = 'E3 2nd sem'
        if data['e3(consolidate)'][0]['pass']==1:
                level = 'E3 Consolidate'
        return level
#teacher controls

#student controls
class Student_by_usn(Resource):
    def get(self,branch,year,usn):
        st_db = client[branch]
        collection_name = year
        student = []
        results = st_db[collection_name].find()
        for data in results:
            if usn==data['usn']:
                student.append({
                    "name":data['name'],
                    "usn":data['usn'],
                    "branch":data['branch'],
                    "year":data['year'],
                    "p":[
                                {"0":"P1 Basics"},
                                {"1":"P2 C"},
                                {"2":"P2 Python"},
                                {"3":"P2 Advance"},
                                {"4":"P3 Java"},
                                {"5":"P4 Java"},
                                {"6":"P3 Python"},
                                {"7":"P4 Python"},
                                {"8":"P5 Cloud series"},
                                {"9":"P5 Full stack"},
                                {"10":"P5 Data analysis"},
                                {"11":"P5 Machine learning"}
                        ],
                        "c":[
                                {"0":"C2 Odd"},
                                {"1":"C2 Even"},
                                {"2":"C3 Odd(III core sub)"},
                                {"3":"C3 Even(IV core sub)"},
                                {"4":"C3 Full(I to IV sub)"},
                                {"5":"C4 Odd(V core sub)"},
                                {"6":"C4 Even(VI core sub)"},
                                {"7":"C4 Full(I to VI sub)"},
                                {"8":"C5 Odd(VII core sub)"},
                                {"9":"C5 Even(VIII core sub)"},
                                {"10":"C5 Full(I to VIII core sub)"}
                        ],
                        "a":[
                                {"0":"A1"},
                                {"1":"A2"},
                                {"2":"A3"}
                        ],
                        "s":[
                                {"4":"S1"},
                                {"5":"S2"},
                                {"6":"S3"}
                        ],
                        "e":[
                                {"7":"E3 (1st sem)"},
                                {"8":"E3 (2nd sem)"},
                                {"9":"E3 (Consolidate)"}
                        ],
                    "marks":[
                        {
                        "programming(Px)":[
                                        {
                                        "p1_basics":{
                                                'mark_obtained':data['p1_basics'][0]['mark_obtained'],
                                                'pass_mark':data['p1_basics'][0]['pass_mark'],
                                                'pass': data['p1_basics'][0]['pass']
                                                }
                                        },
                                        {
                                        "p1_basics":{
                                                'mark_obtained':data['p1_basics'][0]['mark_obtained'],
                                                'pass_mark':data['p1_basics'][0]['pass_mark'],
                                                'pass': data['p1_basics'][0]['pass']
                                                }
                                        },
                                        {
                                        "p2_python":{
                                                'mark_obtained':data['p2_python'][0]['mark_obtained'],
                                                'pass_mark':data['p2_python'][0]['pass_mark'],
                                                'pass': data['p2_python'][0]['pass']
                                                }
                                        },
                                        {
                                        "p2_advance":{
                                                'mark_obtained':data['p2_advance'][0]['mark_obtained'],
                                                'pass_mark':data['p2_advance'][0]['pass_mark'],
                                                'pass': data['p2_advance'][0]['pass']
                                                }
                                        },
                                        {
                                        "p3_java":{
                                                'mark_obtained':data['p3_java'][0]['mark_obtained'],
                                                'pass_mark':data['p3_java'][0]['pass_mark'],
                                                'pass': data['p3_java'][0]['pass']
                                                }
                                        },
                                        {
                                        "p4_java":{
                                                'mark_obtained':data['p4_java'][0]['mark_obtained'],
                                                'pass_mark':data['p4_java'][0]['pass_mark'],
                                                'pass': data['p4_java'][0]['pass']
                                                }
                                        },
                                        {
                                        "p3_python":{
                                                'mark_obtained':data['p3_python'][0]['mark_obtained'],
                                                'pass_mark':data['p3_python'][0]['pass_mark'],
                                                'pass': data['p3_python'][0]['pass']
                                                }
                                        },
                                        {
                                        "p4_python":{
                                                'mark_obtained':data['p4_python'][0]['mark_obtained'],
                                                'pass_mark':data['p4_python'][0]['pass_mark'],
                                                'pass': data['p4_python'][0]['pass']
                                                }
                                        },
                                        {
                                        "p5_cloud_series":{
                                                'mark_obtained':data['p5_cloud_series'][0]['mark_obtained'],
                                                'pass_mark':data['p5_cloud_series'][0]['pass_mark'],
                                                'pass': data['p5_cloud_series'][0]['pass']
                                                }
                                        },
                                        {
                                        "p5_full_stack":{
                                                'mark_obtained':data['p5_full_stack'][0]['mark_obtained'],
                                                'pass_mark':data['p5_full_stack'][0]['pass_mark'],
                                                'pass': data['p5_full_stack'][0]['pass']
                                                }
                                        },
                                        {
                                        "p5_data_analysis":{
                                                'mark_obtained':data['p5_data_analysis'][0]['mark_obtained'],
                                                'pass_mark':data['p5_data_analysis'][0]['pass_mark'],
                                                'pass': data['p5_data_analysis'][0]['pass']
                                                }
                                        },
                                        {
                                        "p5_machine_learning":{
                                                'mark_obtained':data['p5_machine_learning'][0]['mark_obtained'],
                                                'pass_mark':data['p5_machine_learning'][0]['pass_mark'],
                                                'pass': data['p5_machine_learning'][0]['pass']
                                                }
                                        }
                                ]
                        },
                        {
                        "core(Cx)":[
                                        {
                                        "c2_odd":{
                                                'mark_obtained':data['c2_odd'][0]['mark_obtained'],
                                                'pass_mark':data['c2_odd'][0]['pass_mark'],
                                                'pass': data['c2_odd'][0]['pass']
                                                }
                                        },
                                        {
                                        "c2_even":{
                                                'mark_obtained':data['c2_even'][0]['mark_obtained'],
                                                'pass_mark':data['c2_even'][0]['pass_mark'],
                                                'pass': data['c2_even'][0]['pass']
                                                }
                                        },
                                        {
                                        "c3_odd(III core sub)":{
                                                'mark_obtained':data['c3_odd(III core sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c3_odd(III core sub)'][0]['pass_mark'],
                                                'pass': data['c3_odd(III core sub)'][0]['pass']
                                                }
                                        },
                                        {
                                        "c3_even(IV core sub)":{
                                                'mark_obtained':data['c3_even(IV core sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c3_even(IV core sub)'][0]['pass_mark'],
                                                'pass': data['c3_even(IV core sub)'][0]['pass']
                                                }
                                        },
                                        {
                                        "c3_full(I to IV sub)":{
                                                'mark_obtained':data['c3_full(I to IV sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c3_full(I to IV sub)'][0]['pass_mark'],
                                                'pass': data['c3_full(I to IV sub)'][0]['pass']
                                                }
                                        },
                                        {
                                        "c4_odd(V core sub)":{
                                                'mark_obtained':data['c4_odd(V core sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c4_odd(V core sub)'][0]['pass_mark'],
                                                'pass': data['c4_odd(V core sub)'][0]['pass']
                                                }
                                        },
                                        {
                                        "c4_even(VI core sub)":{
                                                'mark_obtained':data['c4_even(VI core sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c4_even(VI core sub)'][0]['pass_mark'],
                                                'pass': data['c4_even(VI core sub)'][0]['pass']
                                                }
                                        },
                                        {
                                        "c4_full(I to VI sub)":{
                                                'mark_obtained':data['c4_full(I to VI sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c4_full(I to VI sub)'][0]['pass_mark'],
                                                'pass': data['c4_full(I to VI sub)'][0]['pass']
                                                }       
                                        },
                                        {
                                        "c5_odd(VII core sub)":{
                                                'mark_obtained':data['c5_odd(VII core sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c5_odd(VII core sub)'][0]['pass_mark'],
                                                'pass': data['c5_odd(VII core sub)'][0]['pass']
                                                }
                                        },
                                        {
                                        "c5_even(VIII core sub)":{
                                                'mark_obtained':data['c5_even(VIII core sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c5_even(VIII core sub)'][0]['pass_mark'],
                                                'pass': data['c5_even(VIII core sub)'][0]['pass']
                                                }
                                        },
                                        {
                                        "c5_full(I to VIII core sub)":{
                                                'mark_obtained':data['c5_full(I to VIII core sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c5_full(I to VIII core sub)'][0]['pass_mark'],
                                                'pass': data['c5_full(I to VIII core sub)'][0]['pass']
                                                }
                                        }
                                ]
                        },
                        {
                        "aptitude(Ax)":[
                                        {
                                        "a1":{
                                                'mark_obtained':data['a1'][0]['mark_obtained'],
                                                'pass_mark':data['a1'][0]['pass_mark'],
                                                'pass': data['a1'][0]['pass']
                                                }
                                        },
                                        {
                                        "a2":{
                                                'mark_obtained':data['a2'][0]['mark_obtained'],
                                                'pass_mark':data['a2'][0]['pass_mark'],
                                                'pass': data['a2'][0]['pass']
                                                }
                                        },
                                        {
                                        "a3":{
                                                'mark_obtained':data['a3'][0]['mark_obtained'],
                                                'pass_mark':data['a3'][0]['pass_mark'],
                                                'pass': data['a3'][0]['pass']
                                                }
                                        }
                                ]
                        },
                        {
                        "soft_skill(Sx)":[
                                        {
                                        "s1":{
                                                'mark_obtained':data['s1'][0]['mark_obtained'],
                                                'pass_mark':data['s1'][0]['pass_mark'],
                                                'pass': data['s1'][0]['pass']
                                                }
                                        },
                                        {
                                        "s2":{
                                                'mark_obtained':data['s2'][0]['mark_obtained'],
                                                'pass_mark':data['s2'][0]['pass_mark'],
                                                'pass': data['s2'][0]['pass']
                                                }
                                        },
                                        {
                                        "s3":{
                                                'mark_obtained':data['s3'][0]['mark_obtained'],
                                                'pass_mark':data['s3'][0]['pass_mark'],
                                                'pass': data['s3'][0]['pass']
                                                }
                                        }
                                ]
                        },
                        {
                        "english(Ex)":[
                                        {
                                        "e3(1st sem)":{
                                                'mark_obtained':data['e3(1st sem)'][0]['mark_obtained'],
                                                'pass_mark':data['e3(1st sem)'][0]['pass_mark'],
                                                'pass': data['e3(1st sem)'][0]['pass']
                                                }
                                        },
                                        {
                                        "e3(2nd sem)":{
                                                'mark_obtained':data['e3(2nd sem)'][0]['mark_obtained'],
                                                'pass_mark':data['e3(2nd sem)'][0]['pass_mark'],
                                                'pass': data['e3(2nd sem)'][0]['pass']
                                                }
                                        },
                                        {
                                        "e3(consolidate)":{
                                                'mark_obtained':data['e3(consolidate)'][0]['mark_obtained'],
                                                'pass_mark':data['e3(consolidate)'][0]['pass_mark'],
                                                'pass': data['e3(consolidate)'][0]['pass']
                                                }
                                        },
                                ]
                        },
                    ],
                        "level":{
                                "PX_level":check_px_level(data),
                                "CX_level":check_cx_level(data),
                                "AX_level":check_ax_level(data),
                                "SX_level":check_sx_level(data),
                                "EX_level":check_ex_level(data)
                        },
                })
        if len(student)==0:
            return {"messsage":"No record found with that usn"}, 400
        return student[0], 200

class Student_mark(Resource):
    def get(self,branch,year):
        st_db = client[branch]
        collection_name = year
        students = []
        results = st_db[collection_name].find()
        for data in results:
            students.append({
                    "name":data['name'],
                    "usn":data['usn'],
                    "branch":data['branch'],
                    "year":data['year'],
                    "marks":[
                        {
                                "programming(Px)":[
                                        {
                                        "p1_basics":{
                                                'mark_obtained':data['p1_basics'][0]['mark_obtained'],
                                                'pass_mark':data['p1_basics'][0]['pass_mark'],
                                                'pass': data['p1_basics'][0]['pass']
                                                }
                                        },
                                        {
                                        "p2_c":{
                                                'mark_obtained':data['p2_c'][0]['mark_obtained'],
                                                'pass_mark':data['p2_c'][0]['pass_mark'],
                                                'pass': data['p2_c'][0]['pass']
                                        }       },
                                        {
                                        "p2_python":{
                                                'mark_obtained':data['p2_python'][0]['mark_obtained'],
                                                'pass_mark':data['p2_python'][0]['pass_mark'],
                                                'pass': data['p2_python'][0]['pass']
                                                }
                                        },
                                        {
                                        "p2_advance":{
                                                'mark_obtained':data['p2_advance'][0]['mark_obtained'],
                                                'pass_mark':data['p2_advance'][0]['pass_mark'],
                                                'pass': data['p2_advance'][0]['pass']
                                                }
                                        },
                                        {
                                        "p3_java":{
                                                'mark_obtained':data['p3_java'][0]['mark_obtained'],
                                                'pass_mark':data['p3_java'][0]['pass_mark'],
                                                'pass': data['p3_java'][0]['pass']
                                                }
                                        },
                                        {
                                        "p4_java":{
                                                'mark_obtained':data['p4_java'][0]['mark_obtained'],
                                                'pass_mark':data['p4_java'][0]['pass_mark'],
                                                'pass': data['p4_java'][0]['pass']
                                                }
                                        },
                                        {
                                        "p3_python":{
                                                'mark_obtained':data['p3_python'][0]['mark_obtained'],
                                                'pass_mark':data['p3_python'][0]['pass_mark'],
                                                'pass': data['p3_python'][0]['pass']
                                                }
                                        },
                                        {
                                        "p4_python":{
                                                'mark_obtained':data['p4_python'][0]['mark_obtained'],
                                                'pass_mark':data['p4_python'][0]['pass_mark'],
                                                'pass': data['p4_python'][0]['pass']
                                                }
                                        },
                                        {
                                        "p5_cloud_series":{
                                                'mark_obtained':data['p5_cloud_series'][0]['mark_obtained'],
                                                'pass_mark':data['p5_cloud_series'][0]['pass_mark'],
                                                'pass': data['p5_cloud_series'][0]['pass']
                                                }
                                        },
                                        {
                                        "p5_full_stack":{
                                                'mark_obtained':data['p5_full_stack'][0]['mark_obtained'],
                                                'pass_mark':data['p5_full_stack'][0]['pass_mark'],
                                                'pass': data['p5_full_stack'][0]['pass']
                                                }
                                        },
                                        {
                                        "p5_data_analysis":{
                                                'mark_obtained':data['p5_data_analysis'][0]['mark_obtained'],
                                                'pass_mark':data['p5_data_analysis'][0]['pass_mark'],
                                                'pass': data['p5_data_analysis'][0]['pass']
                                                }
                                        },
                                        {
                                        "p5_machine_learning":{
                                                'mark_obtained':data['p5_machine_learning'][0]['mark_obtained'],
                                                'pass_mark':data['p5_machine_learning'][0]['pass_mark'],
                                                'pass': data['p5_machine_learning'][0]['pass']
                                                }
                                        },
                                ],
                                "core(Cx)":[
                                        {
                                        "c2_odd":{
                                                'mark_obtained':data['c2_odd'][0]['mark_obtained'],
                                                'pass_mark':data['c2_odd'][0]['pass_mark'],
                                                'pass': data['c2_odd'][0]['pass']
                                                }
                                        },
                                        {
                                        "c2_even":{
                                                'mark_obtained':data['c2_even'][0]['mark_obtained'],
                                                'pass_mark':data['c2_even'][0]['pass_mark'],
                                                'pass': data['c2_even'][0]['pass']
                                                }
                                        },
                                        {
                                        "c3_odd(III core sub)":{
                                                'mark_obtained':data['c3_odd(III core sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c3_odd(III core sub)'][0]['pass_mark'],
                                                'pass': data['c3_odd(III core sub)'][0]['pass']
                                                }
                                        },
                                        {
                                        "c3_even(IV core sub)":{
                                                'mark_obtained':data['c3_even(IV core sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c3_even(IV core sub)'][0]['pass_mark'],
                                                'pass': data['c3_even(IV core sub)'][0]['pass']
                                                }
                                        },
                                        {
                                        "c3_full(I to IV sub)":{
                                                'mark_obtained':data['c3_full(I to IV sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c3_full(I to IV sub)'][0]['pass_mark'],
                                                'pass': data['c3_full(I to IV sub)'][0]['pass']
                                                }
                                        },
                                        {
                                        "c4_odd(V core sub)":{
                                                'mark_obtained':data['c4_odd(V core sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c4_odd(V core sub)'][0]['pass_mark'],
                                                'pass': data['c4_odd(V core sub)'][0]['pass']
                                                }
                                        },
                                        {
                                        "c4_even(VI core sub)":{
                                                'mark_obtained':data['c4_even(VI core sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c4_even(VI core sub)'][0]['pass_mark'],
                                                'pass': data['c4_even(VI core sub)'][0]['pass']
                                                }
                                        },
                                        {
                                        "c4_full(I to VI sub)":{
                                                'mark_obtained':data['c4_full(I to VI sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c4_full(I to VI sub)'][0]['pass_mark'],
                                                'pass': data['c4_full(I to VI sub)'][0]['pass']
                                                }       
                                        },
                                        {
                                        "c5_odd(VII core sub)":{
                                                'mark_obtained':data['c5_odd(VII core sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c5_odd(VII core sub)'][0]['pass_mark'],
                                                'pass': data['c5_odd(VII core sub)'][0]['pass']
                                                }
                                        },
                                        {
                                        "c5_even(VIII core sub)":{
                                                'mark_obtained':data['c5_even(VIII core sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c5_even(VIII core sub)'][0]['pass_mark'],
                                                'pass': data['c5_even(VIII core sub)'][0]['pass']
                                                }
                                        },
                                        {
                                        "c5_full(I to VIII core sub)":{
                                                'mark_obtained':data['c5_full(I to VIII core sub)'][0]['mark_obtained'],
                                                'pass_mark':data['c5_full(I to VIII core sub)'][0]['pass_mark'],
                                                'pass': data['c5_full(I to VIII core sub)'][0]['pass']
                                                }
                                        },
                                ],
                                "aptitude(Ax)":[
                                        {
                                        "a1":{
                                                'mark_obtained':data['a1'][0]['mark_obtained'],
                                                'pass_mark':data['a1'][0]['pass_mark'],
                                                'pass': data['a1'][0]['pass']
                                                }
                                        },
                                        {
                                        "a2":{
                                                'mark_obtained':data['a2'][0]['mark_obtained'],
                                                'pass_mark':data['a2'][0]['pass_mark'],
                                                'pass': data['a2'][0]['pass']
                                                }
                                        },
                                        {
                                        "a3":{
                                                'mark_obtained':data['a3'][0]['mark_obtained'],
                                                'pass_mark':data['a3'][0]['pass_mark'],
                                                'pass': data['a3'][0]['pass']
                                                }
                                        },
                                ],
                                "soft_skill(Sx)":[
                                        {
                                        "s1":{
                                                'mark_obtained':data['s1'][0]['mark_obtained'],
                                                'pass_mark':data['s1'][0]['pass_mark'],
                                                'pass': data['s1'][0]['pass']
                                                }
                                        },
                                        {
                                        "s2":{
                                                'mark_obtained':data['s2'][0]['mark_obtained'],
                                                'pass_mark':data['s2'][0]['pass_mark'],
                                                'pass': data['s2'][0]['pass']
                                                }
                                        },
                                        {
                                        "s3":{
                                                'mark_obtained':data['s3'][0]['mark_obtained'],
                                                'pass_mark':data['s3'][0]['pass_mark'],
                                                'pass': data['s3'][0]['pass']
                                                }
                                        },
                                ],
                                "english(Ex)":[
                                        {
                                        "e3(1st sem)":{
                                                'mark_obtained':data['e3(1st sem)'][0]['mark_obtained'],
                                                'pass_mark':data['e3(1st sem)'][0]['pass_mark'],
                                                'pass': data['e3(1st sem)'][0]['pass']
                                                }
                                        },
                                        {
                                        "e3(2nd sem)":{
                                                'mark_obtained':data['e3(2nd sem)'][0]['mark_obtained'],
                                                'pass_mark':data['e3(2nd sem)'][0]['pass_mark'],
                                                'pass': data['e3(2nd sem)'][0]['pass']
                                                }
                                        },
                                        {
                                        "e3(consolidate)":{
                                                'mark_obtained':data['e3(consolidate)'][0]['mark_obtained'],
                                                'pass_mark':data['e3(consolidate)'][0]['pass_mark'],
                                                'pass': data['e3(consolidate)'][0]['pass']
                                                }
                                        },
                                ]
                        }
                        ],
                        "level":{
                                "PX_level":check_px_level(data),
                                "CX_level":check_cx_level(data),
                                "AX_level":check_ax_level(data),
                                "SX_level":check_sx_level(data),
                                "EX_level":check_ex_level(data)
                        }
                })
        if len(students)==0:
            return {"messsage":"No records found"}, 400
        return students, 200

#student controls

#admin controls
api.add_resource(Admin_auth,'/admin/login')
api.add_resource(Admin,'/admin','/admin/<string:name>')
api.add_resource(Teacher,'/teachers','/teachers/<string:name>')
#admin controls

#teacher login controls
api.add_resource(Teachers_auth,'/teacher/login')
#teacher login controls

#teachers control
api.add_resource(Student,'/students/<string:branch>/<string:year>')
#teachers control

#Student control
api.add_resource(Student_mark,'/get_marks/<string:branch>/<string:year>')
api.add_resource(Student_by_usn,'/get_mark/<string:branch>/<string:year>/<string:usn>')
#student control

if __name__ == '__main__':
    app.run(debug=True)
