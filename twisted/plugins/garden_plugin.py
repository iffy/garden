from twisted.application.service import ServiceMaker

serviceMaker = ServiceMaker('garden', 'garden.twistd.main',
                            'Garden', 'garden')

