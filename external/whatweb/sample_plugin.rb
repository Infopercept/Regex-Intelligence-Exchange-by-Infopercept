##
# This file is part of WhatWeb and may be subject to
# redistribution and commercial restrictions. Please see the WhatWeb
# web site for more information on licensing and terms of use.
# http://www.morningstarsecurity.com/research/whatweb
##
Plugin.define "Sample-Plugin" do
author "WhatWeb Project"
version "0.1"
description "Sample plugin for testing import functionality"

# Matches #
matches [
	# Version detection
	{ :version=>/SampleApp\/([^\s]+)/ },

	# HTTP Server header
	{ :search=>"headers[server]", :regexp=>/^SampleApp\/([0-9\.]+)/ },

	# HTML title
	{ :text=>'<title>Sample Application</title>' },

	# Meta generator tag
	{ :text=>'<meta name="generator" content="SampleApp' },

	# JavaScript variable
	{ :regexp=>/var sampleAppVersion = "([0-9\.]+)";/ },

	# Cookie
	{ :search=>"headers[set-cookie]", :regexp=>/sampleapp_session=/ },

	# CSS file
	{ :text=>'/sampleapp.css' },

	# Powered by text
	{ :text=>'Powered by SampleApp' },
]

end