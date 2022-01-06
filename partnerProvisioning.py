
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


from concurrent import futures
import logging

import grpc

import partnerProvisioning_pb2
import partnerProvisioning_pb2_grpc


class PpsServiceServicer( partnerProvisioning_pb2_grpc.PpsServiceServicer ):
    def PartnerProvisioning( self, request, context ):
        ret_smlctxt = partnerProvisioning_pb2.PpsResponse();
        ret_smlctxt.samlContext.msoServiceId = "MidtownMiami_IP";
        ret_smlctxt.samlContext.serviceTier = "<operator>_MANAGED_NOVOD";
        #ret_smlctxt.samlContext.serviceTier = "<operator>_MAN";
        ret_smlctxt.samlContext.deviceType = request.provisionState.samlContext.deviceType;
        ret_smlctxt.samlContext.partnerCustomerId = request.provisionState.samlContext.partnerCustomerId;
        ret_smlctxt.samlContext.partnerId = request.provisionState.samlContext.partnerId;
        ret_smlctxt.samlContext.streamingEnabled = request.provisionState.samlContext.streamingEnabled;
        ret_smlctxt.samlContext.transactionsEnabled = request.provisionState.samlContext.transactionsEnabled;
        #ret_smlctxt.samlContext.vodSiteId = "PREPRODVOD";
        return ret_smlctxt;


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    partnerProvisioning_pb2_grpc.add_PpsServiceServicer_to_server(
        PpsServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()