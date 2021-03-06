import numpy as np

tempdata=[310,300,290,280,270,260,250,240,230,220,210,200,190,180,170,160,150,140,130,120,110,100,95,90,85,80,77,75,70,65,60,58,56,54,52,50,48,46,44,42,40,38,36,34,32,30,28,26,24,22,21,20,19,18,17,16,15,14,13,12,11,10,9.5,9,8.5,8,7.5,7.25,7,6.75,6.5,6.25,6,5.75,5.5,5.25,5,4.9,4.8,4.7,4.6,4.5,4.4,4.3,4.2,4.1,4,3.9,3.8,3.7,3.6,3.5,3.4,3.3,3.2,3.1,3,2.9,2.8,2.7,2.6,2.5,2.4,2.3,2.2,2.1,2,1.95,1.9,1.85,1.8,1.75,1.7,1.65,1.6,1.55,1.5,1.45,1.4,1.35,1.3,1.25,1.2,1.15,1.1,1.08,1.05,1]

voltdata=[0.53618,0.55967,0.58248,0.60458,0.62665,0.64862,0.67037,0.69169,0.71318,0.73512,0.75674,0.77825,0.79952,0.82057,0.84139,0.86194,0.88228,0.90216,0.92159,0.94065,0.95933,0.97751,0.98646,0.9953,1.00414,1.01283,1.018,1.02146,1.03024,1.03886,1.04731,1.05061,1.05389,1.05701,1.06017,1.06327,1.06626,1.06923,1.07212,1.07544,1.07744,1.08047,1.08337,1.08639,1.08972,1.09202,1.09541,1.10382,1.11522,1.13398,1.14955,1.16619,1.18417,1.20321,1.22439,1.24514,1.26756,1.29081,1.31414,1.33911,1.36959,1.40232,1.421,1.44318,1.46727,1.49213,1.51933,1.53374,1.54799,1.56221,1.5766,1.59068,1.60443,1.61785,1.63278,1.64665,1.66094,1.66654,1.67277,1.67862,1.68485,1.69084,1.69665,1.70226,1.70702,1.71283,1.71862,1.72319,1.72885,1.73317,1.73735,1.74087,1.744,1.7464,1.74949,1.75178,1.75433,1.75723,1.76009,1.76275,1.76527,1.76813,1.77187,1.77431,1.77669,1.77899,1.78111,1.78266,1.78337,1.78426,1.78524,1.78588,1.78721,1.7883,1.7896,1.79059,1.79166,1.79301,1.79425,1.79518,1.79626,1.7974,1.7988,1.80014,1.80107,1.80176,1.80294,1.80364]

splinecoefficient=[-0.002349,-0.002281,-0.00221,-0.002207,-0.002197,-0.002175,-0.002132,-0.002149,-0.002194,-0.002162,-0.002151,-0.002127,-0.002105,-0.002082,-0.002055,-0.002034,-0.001988,-0.001943,-0.001906,-0.001868,-0.001818,-0.00179,-0.001768,-0.001768,-0.001738,-0.001723333,-0.00173,-0.001756,-0.001724,-0.00169,-0.00165,-0.00164,-0.00156,-0.00158,-0.00155,-0.001495,-0.001485,-0.001445,-0.00166,-0.001,-0.001515,-0.00145,-0.00151,-0.001665,-0.00115,-0.001695,-0.004205,-0.0057,-0.00938,-0.01557,-0.01664,-0.01798,-0.01904,-0.02118,-0.02075,-0.02242,-0.02325,-0.02333,-0.02497,-0.03048,-0.03273,-0.03736,-0.04436,-0.04818,-0.04972,-0.0544,-0.05764,-0.057,-0.05688,-0.05756,-0.05632,-0.055,-0.05368,-0.05972,-0.05548,-0.05716,-0.056,-0.0623,-0.0585,-0.0623,-0.0599,-0.0581,-0.0561,-0.0476,-0.0581,-0.0579,-0.0457,-0.0566,-0.0432,-0.0418,-0.0352,-0.0313,-0.024,-0.0309,-0.0229,-0.0255,-0.029,-0.0286,-0.0266,-0.0252,-0.0286,-0.0374,-0.0244,-0.0238,-0.023,-0.0212,-0.031,-0.0142,-0.0178,-0.0196,-0.0128,-0.0266,-0.0218,-0.026,-0.0198,-0.0214,-0.027,-0.0248,-0.0186,-0.0216,-0.0228,-0.028,-0.0268,-0.0186,-0.0345,-0.039333333,-0.014]

v=len(voltdata)

def splinepoint(x):
        """
        if x>0:
                for j in range(0,v):
                        if voltdata[j]<=x<voltdata[j+1]:
                                t=(float(x-voltdata[j]))/float((splinecoefficient[j]))+float(tempdata[j])
                        elif x<voltdata[0]:
                                t=(float(x-voltdata[0]))/float(splinecoefficient[0])+float(tempdata[0])
                        elif x>voltdata[-1]:
                                t=(float(x-voltdata[-1]))/float(splinecoefficient[-1])+float(tempdata[-1])

        elif x<0:
                y=-x
                for j in range(0,v):
                        if y<voltdata[0]:
                                t=-(float(y-voltdata[0]))/float(splinecoefficient[0])-float(tempdata[0])
                        elif y>voltdata[-1]:
                                t=-(float(y-voltdata[-1]))/float(splinecoefficient[-1])-float(tempdata[-1])
                        elif voltdata[j]<=y<voltdata[j+1]:
                                t=-(float(y-voltdata[j]))/float(splinecoefficient[j])-float(tempdata[j])

	return t
        """
        t = 0
        if x>0:
                if x<voltdata[0]:
                        t=(float(x-voltdata[0]))/float(splinecoefficient[0])+float(tempdata[0])
                elif x>voltdata[-1]:
                        t=(float(x-voltdata[-1]))/float(splinecoefficient[-1])+float(tempdata[-1])
                else:
                        for j in range(0,v-1):
                                if voltdata[j]<=x<voltdata[j+1]:
                                        t=(float(x-voltdata[j]))/float(splinecoefficient[j])+float(tempdata[j])

        elif x<0:
                y=-x
                if y<voltdata[0]:
                        t=(float(y-voltdata[0]))/float(splinecoefficient[0])+float(tempdata[0])
                elif y>voltdata[-1]:
                        t=(float(y-voltdata[-1]))/float(splinecoefficient[-1])+float(tempdata[-1])
                else:
                        for j in range(0,v-1):
                                if voltdata[j]<=y<voltdata[j+1]:
                                        t=(float(y-voltdata[j]))/float(splinecoefficient[j])+float(tempdata[j])
        return t

def linearspline(ninja):
	splinetemp=[]
	for i in range(0,len(ninja)):
		"""
		if ninja[i]<voltdata[0]:
			t=0
		elif ninja[i]>voltdata[127]:
			t=0
		else:
		"""
		t=splinepoint(ninja[i])
#		print t
		splinetemp=np.append(splinetemp,t)
	return splinetemp


