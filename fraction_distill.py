import numpy as np
def bol(y):
	"""Bottom operating equations for the components.
	function takes vapour compositions(y)::array and returns an array of corresponding liquid compositions(x)"""
	const=np.array([0.0167,0.0111,0.1056])
	x=y+const
	x/=1.133
	return x
def tol(y):
	"""Top operating equations for the components.
	function takes vapour compositions(y)::array and returns an array of corresponding liquid compositions(x)"""
	const=np.array([0.163,0.001,0.002])
	x=y-const
	x/=0.833
	return x
def vap_comp(volatilities,x):
	"""function takes volatilities::array and the liquid_compositions (x)::array and returns the vapour compositions:array"""
	global alpha_x
	alpha_x=volatilities*x
	alpha_total=float(alpha_x.sum())
	y=alpha_x/alpha_total
	return y
def main(xd_ortho,xf_ortho,x):
	count=0
	top_count=0
	while x[0]<xd_ortho:
		y=vap_comp(volatilities,x)
		if x[0]<xf_ortho:
			x=bol(y)
		else:
			top_count+=1
			if top_count==1:
				print("\n",f"Switched to top operating line after the {count}th plate".upper(),"\n")
			x=tol(y)
		count+=1
		print(f"alpha_x{count-1}:",alpha_x)
		print(f"y{count-1}:",y)
		print(f"x{count}:",x)
		print(count, "plates")
	return
if __name__=="__main__":
	xd_ortho=0.98#composition of ortho in the distillate
	xf_ortho=0.6#composition of ortho in the feed
	volatilities=np.array([1.7,1.16,1])
	x=np.array([0.125,0.083,0.792])#mole fraction of the components in the still
	main(xd_ortho,xf_ortho,x)
