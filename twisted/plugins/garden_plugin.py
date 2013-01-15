from twisted.application.service import ServiceMaker

serviceMaker = ServiceMaker('garden', 'garden.twistd', 'Garden Daemons', 
                            'garden')