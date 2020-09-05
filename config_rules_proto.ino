insurer= ORG, NAME, 
insured= ORG, NAME,
valued date= (0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[0-2])/\d\d\d\d,
loss date = (0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[0-2])/\d\d\d\d,
reported date = (0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[0-2])/\d\d\d\d,
status = OPEN,
expense reserve= $?([0-9]{1,3},([0-9]{3},)*[0-9]{3}|[0-9]+)(.[0-9][0-9])?,
expense paid= $?([0-9]{1,3},([0-9]{3},)*[0-9]{3}|[0-9]+)(.[0-9][0-9])?,
indemnity reserve= $?([0-9]{1,3},([0-9]{3},)*[0-9]{3}|[0-9]+)(.[0-9][0-9])?,
indemnity paid= $?([0-9]{1,3},([0-9]{3},)*[0-9]{3}|[0-9]+)(.[0-9][0-9])?,
report date = (19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01]),
broker = None,
expense payments = None,