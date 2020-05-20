##Create a list for all IN IDs and one for all EX IDs
AllIDs_IN=list()
ALLIDs_EX=list()

for pos in range(0,len(FibratesData.Target))
    if FibratesData.Target[pos]==1:
        AllIDs_IN.append(FibratesData.IDs[pos])
    else:
        AllIDs_EX.append(FibratesData.IDs[pos])
