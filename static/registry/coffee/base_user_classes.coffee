root = this

###
   Simple class to store all data related to a proposed change,
   this is left fairly general but is primarily used in user profile
   changing by base_user.coffee.
###
class Change

   constructor: (target, newValue, oldValue, revert, perm) ->
      throw new Error('Reversion must be a function to call for reversion') unless _.isFunction(revert)

      @target = target # Target of change (source object)
      @new = newValue # Replacing value
      @old = oldValue # Repalced value
      @rev = revert # Reversion function
      @perm = perm # Permission required to make change, can be none
      @reverted = no    # State flag

   revert: =>
      @rev(@target, @old) unless @reverted
      @reverted = yes


###
   Represents a simple authentication routine for a visitor to a page. The
   Authenticator is ignorant of the contents of the permissions, only being able
   to do 'in' comparisons.

   Because the nature of ajax requests are asynchronous and it is possible for
   revalidation to occur, using asynchronous functions are recommended when possible,
   otherwise attempting to use synchronous methods like 'has' will cause an error
   to be thrown while validation occurs.
###
class Authenticator
   constructor: (uuid) ->
      @uuid = uuid # uuid of authenticated user
      @perms = [] # List of permissions
      @validating = no # Validating Flag
      @shouldValidate = no # Should Validate Flag
      @revalidate()        # Initial Validation

   has: (perm) =>
      @revalidate if @shouldValidate

      if @validating
         throw new Error('Cannot check permissions while validating!')

      perm in @perms

   use: (callback) =>
      if @shouldValidate
         @revalidate(callback)
      else
         tfn = =>
            processNextTick(tfn) if @validating
            callback?(null, @perms.copy()) unless @validating

         tfn()

   revalidate: (cb) =>
      return if @validating # Don't validate more than once in any instant

      @validating = yes
      @perms = []
      $.ajax
         context: @
         url: "/verify/#{@uuid}"
         type: "GET"
         success: (data) =>
            @perms = (p for own p of data.perms when _.isString(p) and data.perms[p] is true)
            @validating = @shouldValidate = no
            cb?(null, @perms.copy())
         failure: =>
            console.log 'Failed to validate user!'
            @validating = @shouldValidate = no
            cb?(new Error('Could not validate user'))

   reassign: (uuid, cb) =>
      throw new Error('Cannot reassign to undefined uuid.') if uuid?

      @uuid = uuid

      tfn = =>
         if @validating then processNextTick(tfn) else @revalidate(cb)

      tfn()

   checkUser: (uuid) =>
      @uuid is uuid

   commitChanges: (changes, cb) =>
      @use((perms) =>
         possibleChanges = (c for c in changes when not c.perm? or c.perm in perms)
         successes = []
         failures = (c for c in changes when c not in possibleChanges)

         changeData = (new () -> @[$(c.target).date('field')] = c.new for c in possibleChanges $ @)
         changeData = {}
         dataToChange = {}
         changeData[$(c.target).data('field')] = c.new for c in possibleChanges
         dataToChange[$(c.target).data('field')] = c for c in possibleChanges
         $.ajax
            context: @
            url: "/user/#{@uuid}"
            type: 'PATCH'
            data: changeData
            cache: no
            dataType: 'json'
            success: (resp) ->
               console.log("resp: ");
               console.dir(resp);

               successes.push((dataToChange[f] for f in resp.successes))
               failures.push((dataToChange[f] for f in resp.failures))

               cb(null, successes, failures)
            failure: (resp) ->
               console.log("failure")
               console.dir(resp)

               cb(new Error("User updated failed"), null, null)
      )

root.Authenticator = Authenticator
root.Change = Change