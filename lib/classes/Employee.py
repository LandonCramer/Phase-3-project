from datetime import datetime
import helpers
from classes.__init__ import CURSOR, CONN
from classes.Customer import Customer
from classes.Car import Car
from classes.Appointment import Appointment

class Employee:
    def __init__(self, name, salary, hire_date, id_ = None, job_title = None):
        self.name = name
        self.salary = salary
        self.hire_date = hire_date
        self.id_ = id_
        self.job_title = helpers.pascal_to_words(type(self).__name__)
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        if not isinstance(name, str):
            raise TypeError('Name must be a string.')
        elif not name:
            raise ValueError('Name must be a non-empty string.')
        else:
            self._name = name
    
    @property
    def salary(self):
        return self._salary
    
    @salary.setter
    def salary(self, salary):
        if not isinstance(salary, int) or isinstance(salary, bool):
            raise TypeError('Salary must be an integer.')
        elif salary not in range(50_000, 250_001):
            raise ValueError('Salary must be between 50,000 and 250,000.')
        else:
            self._salary = salary

    @property
    def hire_date(self):
        return self._hire_date
    @hire_date.setter
    def hire_date(self, hire_date):
        if isinstance(hire_date, datetime):
            self._hire_date = hire_date
        else:
            raise TypeError('Date must be a valid datetime object.')

    @property
    def id_(self):
        return self._id_ 
    @id_.setter
    def id_(self, id_):
        if not id_:
            self._id_ = None
        elif not isinstance(id_, int) or isinstance(id_, bool):
            raise TypeError("ID must be an integer.")
        else:
            self._id_ = id_

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Employee instances"""
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                salary INTEGER,
                job_title TEXT,
                hire_date TEXT
            )
        """
        CURSOR.execute(sql)
        CONN.commit()
    
    @classmethod
    def drop_table(cls):
        sql = """
            DROP TABLE IF EXISTS employees
        """
        
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def get_all(cls):
        if cls == Employee:
            sql = """
                SELECT * FROM employees
            """
        else:
            sql = f"""
                SELECT * FROM employees
                WHERE job_title = '{helpers.pascal_to_words(cls.__name__)}'
            """     

        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id_):
        CURSOR.execute(
            '''
            SELECT * FROM employees
            WHERE id = ?
            ''',
            (id_,)
        )
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None
    
    def save(self):
        """ Insert a new row with the name, salary, and hire date (hire date converted to a string, Format YYYY-MM-DD) """
        sql = """
            INSERT INTO employees (name, salary, job_title, hire_date)
            VALUES (?, ?, ?, ?)
        """
        CURSOR.execute(sql, (self.name, self.salary, self.job_title, helpers.parse_date(self.hire_date)))
        CONN.commit()

    @classmethod
    def create(cls, name, salary, job_title, hire_date):
        """ Initialize a new Employee instance and save the object to the database """
        employee = cls(name, salary, job_title, hire_date)
        employee.save()
        return employee

    def update(self):
        """ Update the table row corresponding to the current Employee instance """
        sql = """
            UPDATE employees
            SET name = ?, salary = ?, job_title = ?, hire_date = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.salary, self.job_title, self.hire_date, self.id))
        CONN.commit()

    def delete(self):
        """ Delete the table row corresponding to the current Employee instance """
        sql = """
            DELETE FROM employees
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.id,))
        CONN.commit()

#Monday new code
    @classmethod
    def instance_from_db(cls, row):
        return cls(
            row[1], #name
            row[2], #salary
            helpers.parse_date(row[4]), #hire_date
            row[0], #id_
            row[3] #job_title
        )
    
    @classmethod
    def get_employees_by_role(cls, role):
        sql = """
            SELECT *
            FROM employees
            WHERE job_title = ?
        """
        rows = CURSOR.execute(sql, (role,)).fetchall()
        return [cls.instance_from_db(row) for row in rows]
    
    @classmethod
    def employee_of_the_month(cls):
        pass

    def appts(self):
        CURSOR.execute(f"""
            SELECT * FROM appointments
            WHERE employee_id = {self.id_}
            """
            )
        rows = CURSOR.fetchall()
        return [Appointment.instance_from_db(row) for row in rows] if rows else None

    def test_drives(self):
        if self.job_title in ('Salesman', 'Manager'):
            return [appt for appt in self.appts() if appt.type_ == 'TESTDRIVE'] if self.appts() else None
        else:
            raise ValueError(
                'Only Salesmen and Managers have access to Testdrives.'
            )
    
    def services(self):
        if self.job_title in ('Service Tech', 'Manager'):
            return [appt for appt in self.appts() if appt.type_ == 'SERVICE'] if self.appts() else None
        else:
            raise ValueError(
                'Only Service Techs and Managers have access to Services.'
            )
    
    def sales(self):
        if self.job_title in ('Salesman', 'Manager'):
            return [appt for appt in self.appts() if appt.type_ == 'SALE'] if self.appts() else None
        else:
            raise ValueError(
                'Only Service Techs and Managers have access to Sales.'
            )
    
    def customers(self):
        from classes.Customer import Customer
        cust_ids = {appt.customer_id for appt in self.appts()}
        custs = []
        for id_ in cust_ids:
            custs.append(Customer.find_by_id(id_))
        return custs
    
    def cars(self):
        from classes.Car import Car
        car_ids = {appt.car_id for appt in self.appts()}
        cars = []
        for id_ in car_ids:
            cars.append(Car.find_by_id(id_))
        return cars