# Agent Service Exchange

Find participating real-world service providers through your AI assistant.

**Live pilot:** free provider search and expressly authorised private plumbing/heating enquiries to L&G and cleaning enquiries to Sauber mit Sam across all 23 Vienna districts (Austria). No customer account, automatic booking or appointment guarantee. Patrick Kaufmann operates and develops the platform and is the contact for L&G installation enquiries. Sauber mit Sam is operated by Samiha Aktaa; authorised cleaning enquiries go to office@sauber-mit-sam.at. Other opt-in businesses can be searched; general marketplace publication and paid contact purchases are not enabled.

- [Find a service provider](https://api.eucompliance.tools/exchange/info)
- [Connection and tool documentation](https://api.eucompliance.tools/exchange/docs)
- Remote MCP: `https://api.eucompliance.tools/exchange/mcp/`
- Read-only MCP: `https://api.eucompliance.tools/exchange/discover/`
- [Privacy](https://api.eucompliance.tools/exchange/privacy) · [Terms](https://api.eucompliance.tools/exchange/terms) · [Operator and support](https://api.eucompliance.tools/exchange/impressum)

Connect the remote MCP endpoint in an MCP-compatible host. Ask for the service and area; inspect the returned participating providers. Before a direct enquiry, read `direct_installation_inquiry_options` for L&G or `direct_cleaning_inquiry_options` for Sauber mit Sam, explain the named recipient and data use, then obtain explicit permission for the exact details. Never send invented enquiries, unrelated chat history, access codes or health information. The submission receipt is not a booking.

This repository contains public connection metadata and a portable plugin package. The service backend is maintained separately. Inclusion in the open MCP Registry does not mean approval, installation or automatic recommendations by ChatGPT or Claude.

## Publication status

The `plugin/` directory is a submission draft. OpenAI developer identity verification, client acceptance, an accessible demo recording and portal review are still required. Claude has been submitted and is in review; it is not publicly listed yet. No vendor listing or endorsement is claimed.

## Fees

Customer search and direct installation and cleaning enquiries are free. Actual work is separately agreed and billed by the service business. The planned marketplace contact fee is exactly 5 USDC per deliberately selected contact; contact purchases are currently disabled.
