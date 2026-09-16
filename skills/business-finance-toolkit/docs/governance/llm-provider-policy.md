# LLM/provider policy

The toolkit is provider-neutral. A provider may generate a draft summary, identify candidate questions, classify supplied text, or format a decision memo. It cannot be the source of a regulated fact, the sole validator of a calculation, or the approving authority for a decision.

Every integration must declare: provider identity, model/version, data classification allowed to leave the environment, retention terms, prompt/template version, input hash, output identifier, and reviewer. Default policy is deny external transmission of confidential operational, customer, supplier, financial, or personal data until an explicit policy permits it.

All numeric results shown in a decision memo must reference a deterministic calculator result or be labelled as a non-binding estimate with inputs and method.
