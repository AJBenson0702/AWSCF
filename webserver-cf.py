from troposphere import Ref, Template, Parameter, Output, Join, GetAtt, Base64
import troposphere.ec2 as ec2

t = Template()

# Security group
# AMI id and instance type
# SSh Key Pair

sg = ec2.SecurityGroup("lampsg")
sg.GroupDescription = "allow access through port 80 and 22 to the webserver"
sg.SecurityGroupIngress = [
	ec2.SecurityGroupRule(IpProtocol = "tcp", FromPort = "22", ToPort = "22", CidrIp = "0.0.0.0/0"),
	ec2.SecurityGroupRule(IpProtocol = "tcp", FromPort = "80", ToPort = "80", CidrIp = "0.0.0.0/0"),

]

t.add_resource(sg)

keypair = t.add_parameter(Parameter(
	"KeyName",
	Description = "allow ssh key we created",
	Type = "String"
	))

instance = ec2.Instance("webserver")
instance.ImageId = "ami-b70554c8"
instance.InstanceType = "t2.micro"
instance.SecurityGroups = [Ref(sg)]
instance.KeyName = Ref(keypair) 
ud = Base64(Join('\n',
	[	
		"#!/bin/bash",
		"sudo yum -y install httpd",
		"sudo echo '<html><body><h1>Welcome to Devops On AWS</h1></body></html>' > /var/www/html/test.html",
		"sudo systemctl start httpd",
		"sudo systemctl enable http"

	]))

instance.UserData = ud

t.add_resource(instance)

t.add_output(Output(
	"InstanceAccess",
	Description = "Command to use to access the instance using ssh",
	Value = Join("", ["ssh -i ~/.ssh/lampkey.pem ec2-user@",GetAtt(instance, "PublicDnsName")])
	))

t.add_output(Output(
	"WebUrl",
	Description = "The URL of instance",
	Value = Join("",["http:\\",GetAtt(instance, "PublicDnsName")])
	))

print(t.to_json())