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
    @jwt_required
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

    @jwt_required
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

    @jwt_required
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
    @jwt_required
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

    @jwt_required
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

    @jwt_required
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

    @jwt_required
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
            'p1_basics':data['p1_basics'],
            "p2_c":data['p2_c'],
            "p2_python":data['p2_python'],
            "p2_advance":data['p2_advance'],
            "p3_java":data['p3_java'],
            "p4_java":data['p4_java'],
            "p3_python":data['p3_python'],
            "p4_python":data['p4_python'],
            "p5_cloud_series":data['p5_cloud_series'],
            "p5_full_stack":data['p5_full_stack'],
            "p5_data_analysis":data['p5_data_analysis'],
            "p5_machine_learning":data['p5_machine_learning'],
            "c2_odd":data['c2_odd'],
            "c2_even":data['c2_even'],
            "c3_odd(III core sub)":data['c3_odd(III core sub)'],
            "c3_even(IV core sub)":data['c3_even(IV core sub)'],
            "c3_full(I to IV sub)":data['c3_full(I to IV sub)'],
            "c4_odd(V core sub)":data['c4_odd(V core sub)'],
            "c4_even(VI core sub)":data['c4_even(VI core sub)'],
            "c4_full(I to VI sub)":data['c4_full(I to VI sub)'],
            "c5_odd(VII core sub)":data['c5_odd(VII core sub)'],
            "c5_even(VIII core sub)":data['c5_even(VIII core sub)'],
            "c5_full(I to VIII core sub)":data['c5_full(I to VIII core sub)'],
            "a1":data['a1'],
            "a2":data['a2'],
            "a3":data['a3'],
            "s1":data['s1'],
            "s2":data['s2'],
            "s3":data['s3'],
            "e3(1st sem)":data['e3(1st sem)'],
            "e3(2nd sem)":data['e3(2nd sem)'],
            "e3(consolidate)":data['e3(consolidate)']
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
                'p1_basics':data['p1_basics'],
                "p2_c":data['p2_c'],
                "p2_python":data['p2_python'],
                "p2_advance":data['p2_advance'],
                "p3_java":data['p3_java'],
                "p4_java":data['p4_java'],
                "p3_python":data['p3_python'],
                "p4_python":data['p4_python'],
                "p5_cloud_series":data['p5_cloud_series'],
                "p5_full_stack":data['p5_full_stack'],
                "p5_data_analysis":data['p5_data_analysis'],
                "p5_machine_learning":data['p5_machine_learning'],
                "c2_odd":data['c2_odd'],
                "c2_even":data['c2_even'],
                "c3_odd(III core sub)":data['c3_odd(III core sub)'],
                "c3_even(IV core sub)":data['c3_even(IV core sub)'],
                "c3_full(I to IV sub)":data['c3_full(I to IV sub)'],
                "c4_odd(V core sub)":data['c4_odd(V core sub)'],
                "c4_even(VI core sub)":data['c4_even(VI core sub)'],
                "c4_full(I to VI sub)":data['c4_full(I to VI sub)'],
                "c5_odd(VII core sub)":data['c5_odd(VII core sub)'],
                "c5_even(VIII core sub)":data['c5_even(VIII core sub)'],
                "c5_full(I to VIII core sub)":data['c5_full(I to VIII core sub)'],
                "a1":data['a1'],
                "a2":data['a2'],
                "a3":data['a3'],
                "s1":data['s1'],
                "s2":data['s2'],
                "s3":data['s3'],
                "e3(1st sem)":data['e3(1st sem)'],
                "e3(2nd sem)":data['e3(2nd sem)'],
                "e3(consolidate)":data['e3(consolidate)']
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
                    'p1_basics':data['p1_basics'],
                    "p2_c":data['p2_c'],
                    "p2_python":data['p2_python'],
                    "p2_advance":data['p2_advance'],
                    "p3_java":data['p3_java'],
                    "p4_java":data['p4_java'],
                    "p3_python":data['p3_python'],
                    "p4_python":data['p4_python'],
                    "p5_cloud_series":data['p5_cloud_series'],
                    "p5_full_stack":data['p5_full_stack'],
                    "p5_data_analysis":data['p5_data_analysis'],
                    "p5_machine_learning":data['p5_machine_learning'],
                    "c2_odd":data['c2_odd'],
                    "c2_even":data['c2_even'],
                    "c3_odd(III core sub)":data['c3_odd(III core sub)'],
                    "c3_even(IV core sub)":data['c3_even(IV core sub)'],
                    "c3_full(I to IV sub)":data['c3_full(I to IV sub)'],
                    "c4_odd(V core sub)":data['c4_odd(V core sub)'],
                    "c4_even(VI core sub)":data['c4_even(VI core sub)'],
                    "c4_full(I to VI sub)":data['c4_full(I to VI sub)'],
                    "c5_odd(VII core sub)":data['c5_odd(VII core sub)'],
                    "c5_even(VIII core sub)":data['c5_even(VIII core sub)'],
                    "c5_full(I to VIII core sub)":data['c5_full(I to VIII core sub)'],
                    "a1":data['a1'],
                    "a2":data['a2'],
                    "a3":data['a3'],
                    "s1":data['s1'],
                    "s2":data['s2'],
                    "s3":data['s3'],
                    "e3(1st sem)":data['e3(1st sem)'],
                    "e3(2nd sem)":data['e3(2nd sem)'],
                    "e3(consolidate)":data['e3(consolidate)']
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
                "vtu_result":data['vtu_result'],
                "year":year,
                "marks":[
                    {
                        "programming(Px)":[
                            {
                                "p1_basics":data['p1_basics'],
                                "p2_c":data['p2_c'],
                                "p2_python":data['p2_python'],
                                "p2_advance":data['p2_advance'],
                                "p3_java":data['p3_java'],
                                "p4_java":data['p4_java'],
                                "p3_python":data['p3_python'],
                                "p4_python":data['p4_python'],
                                "p5_cloud_series":data['p5_cloud_series'],
                                "p5_full_stack":data['p5_full_stack'],
                                "p5_data_analysis":data['p5_data_analysis'],
                                "p5_machine_learning":data['p5_machine_learning']
                            }
                        ],
                        "core(Cx)":[
                            {
                                "c2_odd":data['c2_odd'],
                                "c2_even":data['c2_even'],
                                "c3_odd(III core sub)":data['c3_odd(III core sub)'],
                                "c3_even(IV core sub)":data['c3_even(IV core sub)'],
                                "c3_full(I to IV sub)":data['c3_full(I to IV sub)'],
                                "c4_odd(V core sub)":data['c4_odd(V core sub)'],
                                "c4_even(VI core sub)":data['c4_even(VI core sub)'],
                                "c4_full(I to VI sub)":data['c4_full(I to VI sub)'],
                                "c5_odd(VII core sub)":data['c5_odd(VII core sub)'],
                                "c5_even(VIII core sub)":data['c5_even(VIII core sub)'],
                                "c5_full(I to VIII core sub)":data['c5_full(I to VIII core sub)']
                            }
                        ],
                        "aptitude(Ax)":[
                            {
                                "a1":data['a1'],
                                "a2":data['a2'],
                                "a3":data['a3']
                            }
                        ],
                        "soft_skill(Sx)":[
                            {
                                "s1":data['s1'],
                                "s2":data['s2'],
                                "s3":data['s3']
                            }
                        ],
                        "english(Ex)":[
                            {
                                "e3(1st sem)":data['e3(1st sem)'],
                                "e3(2nd sem)":data['e3(2nd sem)'],
                                "e3(consolidate)":data['e3(consolidate)']
                            }
                        ]
                    }
                ]
            })
        if len(students) == 0:
            return {"message":"no data found"}, 404
        return students, 200
#teacher controls

#student controls
class Student_mark(Resource):
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
                    "marks":[
                        {
                            "programming(Px)":[
                                {
                                    "p1_basics":data['p1_basics'],
                                    "p2_c":data['p2_c'],
                                    "p2_python":data['p2_python'],
                                    "p2_advance":data['p2_advance'],
                                    "p3_java":data['p3_java'],
                                    "p4_java":data['p4_java'],
                                    "p3_python":data['p3_python'],
                                    "p4_python":data['p4_python'],
                                    "p5_cloud_series":data['p5_cloud_series'],
                                    "p5_full_stack":data['p5_full_stack'],
                                    "p5_data_analysis":data['p5_data_analysis'],
                                    "p5_machine_learning":data['p5_machine_learning']
                                }
                            ],
                            "core(Cx)":[
                                {
                                    "c2_odd":data['c2_odd'],
                                    "c2_even":data['c2_even'],
                                    "c3_odd(III core sub)":data['c3_odd(III core sub)'],
                                    "c3_even(IV core sub)":data['c3_even(IV core sub)'],
                                    "c3_full(I to IV sub)":data['c3_full(I to IV sub)'],
                                    "c4_odd(V core sub)":data['c4_odd(V core sub)'],
                                    "c4_even(VI core sub)":data['c4_even(VI core sub)'],
                                    "c4_full(I to VI sub)":data['c4_full(I to VI sub)'],
                                    "c5_odd(VII core sub)":data['c5_odd(VII core sub)'],
                                    "c5_even(VIII core sub)":data['c5_even(VIII core sub)'],
                                    "c5_full(I to VIII core sub)":data['c5_full(I to VIII core sub)']
                                }
                            ],
                            "aptitude(Ax)":[
                                {
                                    "a1":data['a1'],
                                    "a2":data['a2'],
                                    "a3":data['a3']
                                }
                            ],
                            "soft_skill(Sx)":[
                                {
                                    "s1":data['s1'],
                                    "s2":data['s2'],
                                    "s3":data['s3']
                                }
                            ],
                            "english(Ex)":[
                                {
                                    "e3(1st sem)":data['e3(1st sem)'],
                                    "e3(2nd sem)":data['e3(2nd sem)'],
                                    "e3(consolidate)":data['e3(consolidate)']
                                }
                            ]
                        }
                    ]
                })
        if len(student)==0:
            return {"messsage":"No record found with that usn"}, 400
        return student, 200

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
                                "p1_basics":data['p1_basics'],
                                "p2_c":data['p2_c'],
                                "p2_python":data['p2_python'],
                                "p2_advance":data['p2_advance'],
                                "p3_java":data['p3_java'],
                                "p4_java":data['p4_java'],
                                "p3_python":data['p3_python'],
                                "p4_python":data['p4_python'],
                                "p5_cloud_series":data['p5_cloud_series'],
                                "p5_full_stack":data['p5_full_stack'],
                                "p5_data_analysis":data['p5_data_analysis'],
                                "p5_machine_learning":data['p5_machine_learning']
                            }
                        ],
                        "core(Cx)":[
                            {
                                "c2_odd":data['c2_odd'],
                                "c2_even":data['c2_even'],
                                "c3_odd(III core sub)":data['c3_odd(III core sub)'],
                                "c3_even(IV core sub)":data['c3_even(IV core sub)'],
                                "c3_full(I to IV sub)":data['c3_full(I to IV sub)'],
                                "c4_odd(V core sub)":data['c4_odd(V core sub)'],
                                "c4_even(VI core sub)":data['c4_even(VI core sub)'],
                                "c4_full(I to VI sub)":data['c4_full(I to VI sub)'],
                                "c5_odd(VII core sub)":data['c5_odd(VII core sub)'],
                                "c5_even(VIII core sub)":data['c5_even(VIII core sub)'],
                                "c5_full(I to VIII core sub)":data['c5_full(I to VIII core sub)']
                            }
                        ],
                        "aptitude(Ax)":[
                            {
                                "a1":data['a1'],
                                "a2":data['a2'],
                                "a3":data['a3']
                            }
                        ],
                        "soft_skill(Sx)":[
                            {
                                "s1":data['s1'],
                                "s2":data['s2'],
                                "s3":data['s3']
                            }
                        ],
                        "english(Ex)":[
                            {
                                "e3(1st sem)":data['e3(1st sem)'],
                                "e3(2nd sem)":data['e3(2nd sem)'],
                                "e3(consolidate)":data['e3(consolidate)']
                            }
                        ]
                    }
                ]
            })
        if len(students)==0:
            return {"messsage":"No record found with that usn"}, 400
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
api.add_resource(Student,'/students/<string:branch>/<string:year>','/students/<string:branch>/<string:year>/<string:usn>')
#teachers control

#Student control
api.add_resource(Student_mark,'/get_mark/<string:branch>/<string:year>/<string:usn>','/get_mark/<string:branch>/<string:year>')
#student control

if __name__ == '__main__':
    app.run(debug=True)