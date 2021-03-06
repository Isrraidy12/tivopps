#This is provided as an EXAMPLE implementation of the Partner Provisioning API and should NOT be used
#in any production facility as it has not been formally tested, code reviewed, nor has any security audit been
#performed.
#
#The code is provided on an "AS IS" basis, without any WARRANTIES OR CONDITIONS OF ANY KIND, either express
#or implied, as to its performance, accuracy, or completeness. Evaluator is advised not to rely, and hereby
#represents that it shall not rely, on this code for any purpose. To the maximum extent permitted by applicable
#law, TiVo Corporation disclaims all warranties, including without limitation any implied warranties of 
#merchantability, fitness for a particular purpose, and noninfringement. The entire risk arising out of the 
#evaluator's use or performance of the code remains with the evaluator. In no event shall TiVo Corporation or 
#its suppliers be liable for any consequential, incidental, direct, indirect, special, punitive, or other 
#damages whatsoever, whether arising in tort (including negligence), contract or any other theory of law 
#(including, without limitation, damages for loss of business profits, business interruption, loss of business 
#information, or other pecuniary loss) arising out of this agreement or evaluator's or any other party's use of 
#or inability to use the code, even if advised of the possiblity of such damages. 
#

This package contains a small Python-based implementation of the TiVo Partner Provisioning Service (PPS).  The code
simply echos back most of the input parameters from the PPS request, providing the needed parameters in the PPS
response to allow a TiVo Client to complete a serviceLogin request into the Hotwire lab.  These parameters include:
  *  msoServiceId = set to the Hotwire PreProd lab's "MidtownMiami_IP" msoServiceId
  *  serviceTier = set to the Hotwire PreProd lab's "HOTWIREDEV_MANAGED_NOVOD" tier
			
Note that commented values are provided for the "HOTWIREDEV_MAN" service tier and the "PREPRODVOD" vodSiteId, for when IP-VOD has been onboarded.

The implementation leverages Google Protocol Buffers for the message definitions, gRPC services (running via Python) for the PPS service logic,
and the Envoy Proxy for gRPC-JSON translation and HTTP 1.1 interaction.  The Envoy service listens on port 8080.  This is configurable via 
the Envoy YAML configuration file.


==========================
To install the PPS service
==========================

* Install the target VM with the latest CentOS/7 release.
* Copy python files and envoy yaml from /echopps directory included with this README file
* Install Python3 and the needed gRPC tools:
sudo yum -y update
sudo yum -y install python3
sudo pip3 install --upgrade pip
python3 -m pip install --upgrade setuptools
pip install grpcio-tools
pip install googleapis-common-protos

* Start the PPS server:
cd to python src files
python3 partnerProvisioning.py &

* To test direct gRPC:
python3

import partnerProvisioning_pb2_grpc
import grpc
import partnerProvisioning_pb2
channel = grpc.insecure_channel('localhost:50051')
stub = partnerProvisioning_pb2_grpc.PpsServiceStub(channel)
ps = partnerProvisioning_pb2.PpsRequest()
ps.provisionState.samlContext.partnerCustomerId = "123456789"
ps.provisionState.samlContext.partnerId = "tivo:pt.5315"
ps.provisionState.samlContext.streamingEnabled = True
ps.provisionState.samlContext.transactionsEnabled = True
ps.provisionState.deviceConfig.deviceType = "managedAndroidTv"
ps.provisionState.deviceConfig.stbConfig.hardwareSerialNumber = "tch_2345672345678345678"
ps.provisionState.caDeviceId = "34567-124321-12353-214235353244"
ps.provisionState.samlToken = "HUGESAMLTOKEN"
ret_saml = stub.PartnerProvisioning(ps)
print(ret_saml.SerializeToString())	

You should see a result like:
b'\nM\x12\x00J\x0fMidtownMiami_IPb\t123456789j\x0ctivo:pt.5315\x8a\x01\x18HOTWIREDEV_MANAGED_NOVOD\x90\x01\x01\x98\x01\x01'

quit()

* Install Envoy proxy:
sudo yum-config-manager --add-repo https://getenvoy.io/linux/rpm/tetrate-getenvoy.repo
sudo yum -y install getenvoy-envoy

* Confirm envoy is installed properly:
envoy --version


* Start the envoy service:
cd to the directory containing the envoy.yaml file
envoy -c envoy.yaml &

* Send PPS requests to:
http://CENTOS_SERVER:8080/pps/partnerProvisioning


curl --request POST \
  --url http://CENTOS_SERVER:8080/pps/partnerProvisioning \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
	"provisionState": {
		"caDeviceId": "4ed6e8cb-24a2-3f7b-bcb5-fa9225d80200",
		"deviceConfig": {
			"stbConfig": {
				"hardwareSerialNumber": "tch_12345678912345"
			},
			"clientAppName": "com.tivo.hydra.app",
			"deviceType": "managedAndroidTv",
			"friendlyName": "hotwire-stg",
			"manufacturer": "TCH",
			"model": "Jade",
			"osVersion": "Android9",
			"screenDpi": "320",
			"screenResolutionHeightPixels": 1080,
			"screenResolutionWidthPixels": 1920
		},
		"samlContext": {
			"deviceType": "managedAndroidTv",
			"partnerCustomerId": "1234567890",
			"partnerId": "tivo:pt.5315",
			"streamingEnabled": true,
			"transactionsEnabled":true
		},
		"samlToken": "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz48c2FtbDJwOlJlc3BvbnNlIHhtbG5zOnNhbWwycD0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOnByb3RvY29sIiBEZXN0aW5hdGlvbj0iaHR0cHM6Ly8iIElEPSJfMThkNTBmMjBmZWFiNDBlMzc3YjdlOGM3Y2QzMmI4MjUiIElzc3VlSW5zdGFudD0iMjAxOS0wNS0xNlQyMTo0NjozNy42MTBaIiBWZXJzaW9uPSIyLjAiPjxzYW1sMjpJc3N1ZXIgeG1sbnM6c2FtbDI9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphc3NlcnRpb24iPmh0dHBzOi8vZGV2aWNlYmluZGluZ3NlcnZpY2UudGl2by5jb20vYXV0aGVudGljYXRpb25Ub2tlbkdldDwvc2FtbDI6SXNzdWVyPjxzYW1sMnA6U3RhdHVzPjxzYW1sMnA6U3RhdHVzQ29kZSBWYWx1ZT0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOnN0YXR1czpTdWNjZXNzIi8+PC9zYW1sMnA6U3RhdHVzPjxzYW1sMjpBc3NlcnRpb24geG1sbnM6c2FtbDI9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphc3NlcnRpb24iIElEPSJfYTE4MjNjY2FmOGQ1MmRhZjE3MjRhMzMwMzUxN2M4MjIiIElzc3VlSW5zdGFudD0iMjAxOS0wNS0xNlQyMTo0NjozNy42MTBaIiBWZXJzaW9uPSIyLjAiPjxzYW1sMjpJc3N1ZXI+aHR0cHM6Ly9kZXZpY2ViaW5kaW5nc2VydmljZS50aXZvLmNvbS9hdXRoZW50aWNhdGlvblRva2VuR2V0PC9zYW1sMjpJc3N1ZXI+PGRzOlNpZ25hdHVyZSB4bWxuczpkcz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnIyI+PGRzOlNpZ25lZEluZm8+PGRzOkNhbm9uaWNhbGl6YXRpb25NZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzEwL3htbC1leGMtYzE0biMiLz48ZHM6U2lnbmF0dXJlTWV0aG9kIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnI3JzYS1zaGExIi8+PGRzOlJlZmVyZW5jZSBVUkk9IiNfYTE4MjNjY2FmOGQ1MmRhZjE3MjRhMzMwMzUxN2M4MjIiPjxkczpUcmFuc2Zvcm1zPjxkczpUcmFuc2Zvcm0gQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwLzA5L3htbGRzaWcjZW52ZWxvcGVkLXNpZ25hdHVyZSIvPjxkczpUcmFuc2Zvcm0gQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzEwL3htbC1leGMtYzE0biMiLz48L2RzOlRyYW5zZm9ybXM+PGRzOkRpZ2VzdE1ldGhvZCBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvMDkveG1sZHNpZyNzaGExIi8+PGRzOkRpZ2VzdFZhbHVlPnFGME5vbS80MkdWNzhndU1EZEJBT1BwSnVwQT08L2RzOkRpZ2VzdFZhbHVlPjwvZHM6UmVmZXJlbmNlPjwvZHM6U2lnbmVkSW5mbz48ZHM6U2lnbmF0dXJlVmFsdWU+TDdtR21EdUZtQ1Arb0NIdFRhYTVHU3Ywdjhqb0NuNmp1aTExOVdLUEpYK08zNkJDSGxXUzhrcFkxM285aW9US2xhdGJmYW1EYWoyZHFXazluUGp4QnNiMjZybWw1b09yRmN5dkVZS0U0QUlVMkJpRFlwUDVwZ3NtVXhxRFYrb0w2UjFycVVJOFVRVlZlaVQ1ZVpRd05OL3hWckU3WFE5MW1HYTloSXZzVFViRjRkbWY0SjVHemtCc0JiaXl5UktTTzdEaU9ieHhWWUJSSUJaYzlRTk1FcDJoclZZUHU0RVFORVJtQmNCTmlOaXNyRnFrMVBQWVRhT2hTOXJBVlZGRndJaXdZaUhQbG5ySzhQSmdNRXBZTzQ3L3VlczVSZDZQajRrdWd2S3lGeWdwSHZCa01Ednc1ayswZUxDVThaWkc3dDNlRjErUWVrN3RJMVJIQ0NxUVFBPT08L2RzOlNpZ25hdHVyZVZhbHVlPjxkczpLZXlJbmZvPjxkczpYNTA5RGF0YT48ZHM6WDUwOUNlcnRpZmljYXRlPk1JSUUrekNDQStPZ0F3SUJBZ0lCQnpBTkJna3Foa2lHOXcwQkFRc0ZBRENCbHpFUE1BMEdBMVVFQnd3R1FXeDJhWE52TVJNd0VRWUQKVlFRSURBcERZV3hwWm05eWJtbGhNUXN3Q1FZRFZRUUdFd0pWVXpFU01CQUdBMVVFQ2d3SlZHbFdieUJEYjNKd01Rc3dDUVlEVlFRSwpEQUpKVkRFaU1DQUdBMVVFQXd3WlZHbFdieUJKYm5SbGNtNWhiQ0JEYjJSbFUybG5iaUJEUVRFZE1Cc0dDU3FHU0liM0RRRUpBUllPClkyVnlkSE5BZEdsMmJ5NWpiMjB3SGhjTk1UZ3dOVE13TWpFd01qSTJXaGNOTWpNd05UTXdNakV3TWpJMldqQ0JzVEVxTUNnR0ExVUUKU0F3aFUzVndjRzl5ZEdsdVp5QkJjSEJzYVdOaGRHbHZiaUJRY205a2RXTjBhVzl1TVFzd0NRWURWUVFHRXdKVlV6RVRNQkVHQTFVRQpDQXdLUTJGc2FXWnZjbTVwWVRFUE1BMEdBMVVFQnd3R1FXeDJhWE52TVJNd0VRWURWUVFLREFwVWFWWnZJRU52Y25BdU1Sd3dHZ1lEClZRUUxEQk5UWlhKMmFXTmxJRVZ1WjJsdVpXVnlhVzVuTVIwd0d3WURWUVFEREJSRVpYWnBZMlZDYVc1a2FXNW5VMlZ5ZG1salpUQ0MKQVNJd0RRWUpLb1pJaHZjTkFRRUJCUUFEZ2dFUEFEQ0NBUW9DZ2dFQkFMVlFzQ2xFNGxHVllxMy9yQVJPUXZuZkthdGdtN21SRTJEZQpvMkF3dStJKzFYRXpmZU9NSitUQmhkWjhEZGhod0NiVVBObUNEbzlYRWRmb2RORWxNQTAwNnhVNEc3UW9FVkVDemxzc2ZLSXFsbHNkClhlTEFKcWxObXY3STZlSmdCMU1WcDNQN01RWGs4cmNxak5rbzQxcnlMclRYaDdZNFFWa29HOG1kbTkzekdqM29Ec2dkcmF4WElOMEEKYlE0T3ZzVENSMkFHNncveHVLYUcwVTR6TXFsSC9KKy9zRUJuZUpnRDhzSUZhbERNRU55akpPbzlQdUczaEpvYTI3NFAyek4rSEIwMApneXVSMWpUbEVNZXhOaUxNUi8zb0hmbGhXTnZPRTFUV3dNRERVY01uajdvYXZNeXhyNEg4eElJT2ZPYVRscndXYlBQU1ZMcy9YSzhNCkFiY0NBd0VBQWFPQ0FUUXdnZ0V3TUIwR0ExVWREZ1FXQkJUOXFtRkptY3JmQzVVWW9ab0tLUFUySzFsTkd6QWZCZ05WSFNNRUdEQVcKZ0JSaURvWnJuVjNkMzhyVXZlckFKWmdkWFY5Ty9UQWRCZ05WSFNVRUZqQVVCZ2dyQmdFRkJRY0RBZ1lJS3dZQkJRVUhBd013RGdZRApWUjBQQVFIL0JBUURBZ0dDTUVJR0ExVWRId1E3TURrd042QTFvRE9HTVdoMGRIQTZMeTl3YTJrdWRHbDJieTVqYjIwdlZHbFdiMTlKCmJuUmxjbTVoYkY5RGIyUmxVMmxuYmw5RFFTNWpjbXd3ZXdZSUt3WUJCUVVIQVFFRWJ6QnRNQ1FHQ0NzR0FRVUZCekFCaGhob2RIUncKT2k4dmNHdHBMblJwZG04dVkyOXRMMjlqYzNBd1JRWUlLd1lCQlFVSE1BS0dPV2gwZEhBNkx5OXdhMmt1ZEdsMmJ5NWpiMjB2WTJGagpaWEowY3k5VWFWWnZYMGx1ZEdWeWJtRnNYME52WkdWVGFXZHVYME5CTG1OeWREQU5CZ2txaGtpRzl3MEJBUXNGQUFPQ0FRRUFiblU1CjZMRXdONnBaNlFJaTBtYmNJYlhTV2JtcXZvVlJkTnl3RmFWYWlmSm1TMm9jbWFidnI4QjZkTWloYmZjdWtlcFBqME1NYmphS3RJTmIKS24xemlTVmN4SVpvcTJmSnR3YnlyRlZRRkxoSEYwcGNjQktqaDdRcWZUd0FPdi9Jb2N2aFIxOEpzUUpFWEVqMEFRbE1mcnhqM3Z5VwpFSEpCUEpwalROS3FnOGtmaVk1TXlzcUpUWGVxaWVFbDVBbU5ia3pmL2taNHBhakM3RURwK0VaTUdoTHFwWkxFQVhWeUJqeUFkM0lECnZQWW54UmF0OUo2NnFDT21nWFE2MURXblRPelJJU0N0azVvMUhINWtVOTk2c0VKdzZ2VjczanpwQm9KZlJJZjJsTGV5L1ZHTWFBTTMKQzgxTjF0MGlldjBYcEQ5V1hPaXovalhOb3ZIcDQ3eUVxZz09PC9kczpYNTA5Q2VydGlmaWNhdGU+PC9kczpYNTA5RGF0YT48L2RzOktleUluZm8+PC9kczpTaWduYXR1cmU+PHNhbWwyOlN1YmplY3Q+PHNhbWwyOk5hbWVJRCBGb3JtYXQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDpuYW1laWQtZm9ybWF0OnRyYW5zaWVudCI+MTQ5NjliMTMtOGMyNC00ODM2LWFmMDktOWVhODg4OWY0ZDkzPC9zYW1sMjpOYW1lSUQ+PHNhbWwyOlN1YmplY3RDb25maXJtYXRpb24gTWV0aG9kPSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6Y206YmVhcmVyIj48c2FtbDI6U3ViamVjdENvbmZpcm1hdGlvbkRhdGEgTm90T25PckFmdGVyPSIyMDE5LTA2LTE1VDIxOjQ2OjM3LjYxMFoiLz48L3NhbWwyOlN1YmplY3RDb25maXJtYXRpb24+PC9zYW1sMjpTdWJqZWN0PjxzYW1sMjpDb25kaXRpb25zIE5vdEJlZm9yZT0iMjAxOS0wNS0xNlQyMTo0NjoyNy42MTBaIiBOb3RPbk9yQWZ0ZXI9IjIwMTktMDYtMTVUMjE6NDY6MzcuNjEwWiIvPjxzYW1sMjpBdXRoblN0YXRlbWVudCBBdXRobkluc3RhbnQ9IjIwMTktMDUtMTZUMjE6NDY6MzcuNjEwWiIgU2Vzc2lvbkluZGV4PSI2YjRmMzE0Mi00NTIyLTQyYmItYmI4Zi1hODY1ZGEwOTEyMDEiIFNlc3Npb25Ob3RPbk9yQWZ0ZXI9IjIwMTktMDYtMTVUMjE6NDU6MzcuNjEwWiI+PHNhbWwyOkF1dGhuQ29udGV4dD48c2FtbDI6QXV0aG5Db250ZXh0Q2xhc3NSZWY+dXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmFjOmNsYXNzZXM6SW50ZXJuZXRQcm90b2NvbDwvc2FtbDI6QXV0aG5Db250ZXh0Q2xhc3NSZWY+PC9zYW1sMjpBdXRobkNvbnRleHQ+PC9zYW1sMjpBdXRoblN0YXRlbWVudD48c2FtbDI6QXR0cmlidXRlU3RhdGVtZW50PjxzYW1sMjpBdHRyaWJ1dGUgTmFtZT0icGFydG5lcklkIj48c2FtbDI6QXR0cmlidXRlVmFsdWU+NTA4NDwvc2FtbDI6QXR0cmlidXRlVmFsdWU+PC9zYW1sMjpBdHRyaWJ1dGU+PHNhbWwyOkF0dHJpYnV0ZSBOYW1lPSJzdWJzY3JpYmVyOmlkZW50aWZpZXIiPjxzYW1sMjpBdHRyaWJ1dGVWYWx1ZT45OTk5OTk5OTk5ODg4ODg4ODg4PC9zYW1sMjpBdHRyaWJ1dGVWYWx1ZT48L3NhbWwyOkF0dHJpYnV0ZT48c2FtbDI6QXR0cmlidXRlIE5hbWU9InBhcnRuZXJDdXN0b21lcklkIj48c2FtbDI6QXR0cmlidXRlVmFsdWU+OTk5OTk5OTk5OTg4ODg4ODg4ODwvc2FtbDI6QXR0cmlidXRlVmFsdWU+PC9zYW1sMjpBdHRyaWJ1dGU+PC9zYW1sMjpBdHRyaWJ1dGVTdGF0ZW1lbnQ+PC9zYW1sMjpBc3NlcnRpb24+PC9zYW1sMnA6UmVzcG9uc2U+"
	}
}'


You should see a 200 OK response with the following payload:
{
  "samlContext": {
    "deviceType": "managedAndroidTv",
    "msoServiceId": "MidtownMiami_IP",
    "partnerCustomerId": "1234567890",
    "partnerId": "tivo:pt.5315",
    "serviceTier": "HOTWIREDEV_MANAGED_NOVOD",
    "streamingEnabled": true,
    "transactionsEnabled": true
  }
}


#####


