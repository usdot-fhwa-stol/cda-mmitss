from confluent_kafka import Consumer,KafkaException
import BasicVehicle
import json
import socket

class MMITSSConsumer(Consumer):
    def __init__(self,kind,consumerConfigFilename=None,socketConfigFilename=None):
        # Configuration for the Kafka consumer
        self.kind = kind
        consumerConf,topics = self.readConsumerConfig(consumerConfigFilename) 
        
        # Initialize the base class (Consumer)

        super().__init__(consumerConf)
        self.config = self.readSocketConfig(socketConfigFilename)
        self.subscribe(topics)

    def readSocketConfig(self,filename=None):
        # Read a config file into a json object:
        if filename is not None:
            configFile = open(filename, 'r')
        else:
            configFile = open("/nojournal/bin/mmitss-phase3-master-config.json", 'r')
        config = (json.load(configFile))
        configFile.close()
        return config
    
    def readConsumerConfig(self,filename=None):
        # Read a config file into a json object:
        if filename is not None:
            configFile = open(filename, 'r')
        else:
            configFile = open("/nojournal/bin/kafkaConfig.json", 'r')
        config = (json.load(configFile))
        configFile.close()
        topics = config["CONSUMER_TOPICS"][self.kind]
        broker = config["BOOTSTRAP_SERVER"]
        groupId = config["GROUP_ID"]
        consumerConfig = {
            'bootstrap.servers': broker,
            'group.id': groupId,
            'auto.offset.reset': 'earliest',
        }
        return consumerConfig,[topics]
        
        
    def broadcastMsg(self):

        """
        Start consuming messages and invoke the callback for each message.
        """
        try:
            while True:
                msg = self.poll(1.0)  # Poll for messages, with a timeout of 1 second
                if msg is None:
                    continue
                if msg.error():
                    print(f"Error: {msg.error()}")
                    continue

                # Invoke the callback for each message
                self.callback(msg)

        except KeyboardInterrupt:
            pass
        finally:
            self.close()

    def callback(self,msg):
        hostIp = self.config["HostIp"]
        port = self.config["PortNumber"]["MessageTransceiver"]["MessageDecoder"]
        if self.kind == "SRM":
            receivingPort = self.config["PortNumber"]["PriorityRequestServer"]
            msg = self.decodeSRM(msg)
        elif self.kind == "BSM":
            receivingPort = ["PortNumber"]["TrajectoryAware"]
            msg = self.decodeBSM(msg)

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((hostIp,port))
        communicationInfo = (hostIp, receivingPort)
        s.sendto(msg.encode(),communicationInfo)
        s.close()
    def decodeSRM(self, msg):
        return msg

    def decodeBSM(self, msg):
        
        tempID = int(msg["id"],16)
        basicVehicle.tempID
        secMarkSecond = int(msg["sec_mark"])
        basicVehicle.secMarkSecond
        longitudeDecimalDegree = int(msg["lat"])/1000000
        basicVehicle.longitudeDecimalDegree
        latitudeDecimalDegree = int(msg["lat"])/1000000
        basicVehicle.latitudeDecimalDegree
        elevationMeter = int(msg["elev"])
        basicVehicle.elevationMeter
        speedMeterPerSecond = int(msg["speed"])*0.02
        basicVehicle.speedMeterPerSecond
        headingDegree = int(msg["heading"])*0.0125
        basicVehicle.headingDegree
        #vehicle type not defined in Carma Streets BSM
        vehicleType = 0
        basicVehicle.vehicleType
        msg = basicVehicle.basicVehicle2Json()
        
        return msg