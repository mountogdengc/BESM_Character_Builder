import traceback

try:
    import besm_app
    # This will call besm_app.__init__ and should show errors
except Exception as e:
    print("===== ERROR DETAILS =====")
    traceback.print_exc()
    print("=========================")
